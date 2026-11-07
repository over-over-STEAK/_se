const enc = new TextEncoder();
const hex = bytes => [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
const random = () => hex(crypto.getRandomValues(new Uint8Array(32)));
const digest = async s => hex(await crypto.subtle.digest('SHA-256',enc.encode(s)));
const json=(data,status=200,headers={})=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...headers}});
const fail=(message,status=400)=>{throw Object.assign(new Error(message),{status})};
const all=async(db,sql,...args)=>(await db.prepare(sql).bind(...args).all()).results;
const first=(db,sql,...args)=>db.prepare(sql).bind(...args).first();
async function passwordHash(password,salt){const key=await crypto.subtle.importKey('raw',enc.encode(password),'PBKDF2',false,['deriveBits']);return hex(await crypto.subtle.deriveBits({name:'PBKDF2',salt:Uint8Array.from(salt.match(/../g),v=>parseInt(v,16)),iterations:100000,hash:'SHA-256'},key,256))}
async function equal(a,b){return await digest(a)===await digest(b)}
function cookie(req,value,age=28800){return `session=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${age}${new URL(req.url).protocol==='https:'?'; Secure':''}`}
async function session(req,db){const token=(req.headers.get('Cookie')||'').match(/(?:^|;\s*)session=([a-f0-9]{64})(?:;|$)/)?.[1];if(!token)return null;return first(db,'SELECT s.*,u.name,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?',await digest(token),Math.floor(Date.now()/1000))}
async function handler(req,env){
 const url=new URL(req.url),path=url.pathname,db=env.DB;
 if(!path.startsWith('/api/')){const result=await env.ASSETS.fetch(req);const response=new Response(result.body,result);response.headers.set('X-Content-Type-Options','nosniff');response.headers.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'");return response}
 if(!db)fail('資料庫尚未綁定',503);
 if(req.method==='GET'&&path==='/api/state'){
  const s=await session(req,db);if(!s)fail('請先登入',401);
  const [courses,selected,grades,notices]=await Promise.all([
   all(db,'SELECT c.*,(SELECT count(*) FROM enrollments e WHERE e.course_id=c.id) AS enrolled FROM courses c'),
   all(db,'SELECT course_id FROM enrollments WHERE user_id=?',s.user_id),
   all(db,'SELECT name,credits,score,term FROM grades WHERE user_id=?',s.user_id),all(db,'SELECT * FROM notices ORDER BY id DESC')]);
  return json({user:{id:s.user_id,name:s.name,role:s.role},courses,selected:selected.map(x=>x.course_id),grades,notices,csrf:s.csrf});
 }
 if(req.method!=='POST')fail('找不到 API',404);
 const origin=req.headers.get('Origin');if(origin&&origin!==url.origin)fail('不允許跨網站操作',403);
 if(!req.headers.get('Content-Type')?.startsWith('application/json'))fail('需要 JSON 格式',415);
 if(Number(req.headers.get('Content-Length')||0)>16000)fail('資料過大',413);
 const reader=req.body?.getReader();if(!reader)fail('沒有輸入資料');let bytes=0,chunks=[];
 while(true){const {done,value}=await reader.read();if(done)break;bytes+=value.length;if(bytes>16000){await reader.cancel();fail('資料過大',413)}chunks.push(value)}
 let data;try{data=JSON.parse(await new Blob(chunks).text())}catch{fail('輸入格式不正確')}
 if(!data||typeof data!=='object'||Array.isArray(data))fail('輸入格式不正確');
 if(path==='/api/login'){
  const {id,password}=data;if(typeof id!=='string'||typeof password!=='string'||password.length>256||id.length>80)fail('帳號或密碼格式不正確');
  const now=Math.floor(Date.now()/1000),bucket=Math.floor(now/600),ip=req.headers.get('CF-Connecting-IP')||'local';
  const key=await digest(ip+':'+bucket);
  await db.prepare('INSERT INTO login_limits(key,count,expires) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1').bind(key,now+1200).run();
  const limit=await first(db,'SELECT count FROM login_limits WHERE key=?',key);if(limit.count>30)fail('嘗試次數過多，請稍後再試',429);
  const u=await first(db,'SELECT * FROM users WHERE id=?',id);let valid=false;
  if(u?.role==='admin'){if(!env.ADMIN_PASSWORD||env.ADMIN_PASSWORD.length<12)fail('管理員密碼尚未設定（至少 12 字元）',503);valid=await equal(password,env.ADMIN_PASSWORD)}
  else if(u)valid=await equal(await passwordHash(password,u.salt),u.password);
  if(!valid)fail('帳號或密碼錯誤',401);
  const token=random(),csrf=random();
  await db.batch([db.prepare('DELETE FROM sessions WHERE expires<=?').bind(now),db.prepare('DELETE FROM login_limits WHERE expires<=?').bind(now),db.prepare('INSERT INTO sessions(token_hash,user_id,csrf,expires) VALUES(?,?,?,?)').bind(await digest(token),id,csrf,now+28800)]);
  return json({ok:true},200,{'Set-Cookie':cookie(req,token)});
 }
 const s=await session(req,db);if(!s)fail('登入已過期，請重新登入',401);
 if(!await equal(req.headers.get('X-CSRF-Token')||'',s.csrf))fail('請重新整理後再試',403);
 if(path==='/api/logout'){await db.prepare('DELETE FROM sessions WHERE token_hash=?').bind(s.token_hash).run();return json({ok:true},200,{'Set-Cookie':cookie(req,'',0)})}
 if(path==='/api/enroll'||path==='/api/drop'){
  if(s.role!=='student')fail('此功能僅限學生',403);const cid=data.course_id;if(typeof cid!=='string')fail('課程格式不正確');
  if(!await first(db,'SELECT id FROM courses WHERE id=?',cid))fail('課程不存在',404);
  if(path==='/api/drop')await db.prepare('DELETE FROM enrollments WHERE user_id=? AND course_id=?').bind(s.user_id,cid).run();
  else try{await db.prepare('INSERT INTO enrollments(user_id,course_id) VALUES(?,?)').bind(s.user_id,cid).run()}
  catch(e){const message=String(e.message);for(const [marker,text] of [['duplicate_course','已選過此課程'],['schedule_conflict','此課程與已選課程衝堂'],['credit_limit','超過模擬學分上限 25 學分'],['course_full','課程名額已滿']])if(message.includes(marker))fail(text,409);throw e}
 }else if(path==='/api/notice'){
  if(s.role!=='admin')fail('需要管理員權限',403);
  const {title,body}=data;if(typeof title!=='string'||typeof body!=='string'||!title.trim()||title.length>80||!body.trim()||body.length>2000)fail('標題需 1–80 字，內容需 1–2000 字');
  const date=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Taipei'}).format(new Date());
  await db.prepare('INSERT INTO notices(title,body,date) VALUES(?,?,?)').bind(title.trim(),body.trim(),date).run();
 }else if(path==='/api/notice/delete'){
  if(s.role!=='admin')fail('需要管理員權限',403);if(!Number.isInteger(data.id))fail('公告編號不正確');await db.prepare('DELETE FROM notices WHERE id=?').bind(data.id).run();
 }else fail('找不到 API',404);
 return json({ok:true});
}
export default {async fetch(req,env){try{return await handler(req,env)}catch(e){if(!e.status)console.error('API failure',e.message);return json({error:e.status?e.message:'服務暫時無法處理，請確認 D1 已完成初始化'},e.status||500)}}};
