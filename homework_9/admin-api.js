import {inputError as error,requiredText as text,boundedInteger as integer,courseValues,gradeValues} from './validation.js';
const rows=async(db,sql,...args)=>(await db.prepare(sql).bind(...args).all()).results;
export async function adminRead(db){
 const [students,courses,enrollments,grades,notices]=await Promise.all([
 rows(db,"SELECT id,name FROM users WHERE role='student' ORDER BY id"),
 rows(db,'SELECT c.*,(SELECT count(*) FROM enrollments e WHERE e.course_id=c.id) AS enrolled FROM courses c ORDER BY id'),
 rows(db,'SELECT e.user_id,u.name AS student_name,e.course_id,c.name AS course_name,c.credits FROM enrollments e JOIN users u ON u.id=e.user_id JOIN courses c ON c.id=e.course_id ORDER BY e.course_id,e.user_id'),
 rows(db,'SELECT g.user_id,u.name AS student_name,g.name,g.credits,g.score,g.term FROM grades g JOIN users u ON u.id=g.user_id ORDER BY g.term DESC,g.user_id,g.name'),
 rows(db,'SELECT * FROM notices ORDER BY id DESC')]);
 return {students,courses,enrollments,grades,notices};
}
export async function adminWrite(path,data,db){
 try{
  if(path==='/api/admin/course/save'){
   const values=courseValues(data),id=values[0];
   if(data.mode==='create'){
    if(await db.prepare('SELECT id FROM courses WHERE id=?').bind(id).first())error('課號已存在',409);
    await db.prepare('INSERT INTO courses(id,name,teacher,credits,day,period,room,capacity) VALUES(?,?,?,?,?,?,?,?)').bind(...values).run();
   }else if(data.mode==='update'){
    const r=await db.prepare('UPDATE courses SET name=?,teacher=?,credits=?,day=?,period=?,room=?,capacity=? WHERE id=?').bind(...values.slice(1),id).run();
    if(!r.meta.changes)error('課程不存在',404);
   }else error('操作類型錯誤');
  }else if(path==='/api/admin/course/delete'){
   const id=text(data.id,20);const r=await db.prepare('DELETE FROM courses WHERE id=?').bind(id).run();if(!r.meta.changes)error('課程不存在',404);
  }else if(path==='/api/admin/grade/save'){
   const values=gradeValues(data),uid=values[0];
   if(!await db.prepare("SELECT id FROM users WHERE id=? AND role='student'").bind(uid).first())error('學生不存在',404);
   await db.prepare('INSERT INTO grades(user_id,name,credits,score,term) VALUES(?,?,?,?,?) ON CONFLICT(user_id,name,term) DO UPDATE SET credits=excluded.credits,score=excluded.score').bind(...values).run();
  }else if(path==='/api/admin/notice/update'){
   const r=await db.prepare('UPDATE notices SET title=?,body=? WHERE id=?').bind(text(data.title,80),text(data.body,2000),integer(data.id,1,2147483647)).run();if(!r.meta.changes)error('公告不存在',404);
  }else error('找不到管理 API',404);
 }catch(e){
  for(const [code,message] of [['course_has_students','已有學生選課，不能刪除課程'],['occupied_schedule_locked','已有學生選課，不能修改時段或學分；可修改課名、教師、教室與容量'],['capacity_below_enrolled','容量不可低於目前選課人數']])if(String(e.message).includes(code))error(message,409);
  if(String(e.message).includes('UNIQUE constraint'))error('資料已存在，請重新整理後再試',409);
  throw e;
 }
 return {ok:true};
}
