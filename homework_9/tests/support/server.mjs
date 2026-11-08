/** Runs the real Worker handler over HTTP. SQLite implements the D1 binding contract.
 * This is a local test adapter, not the Cloudflare edge runtime. No production data.
 */
import {DatabaseSync} from 'node:sqlite';
import {createServer} from 'node:http';
import {readFileSync,readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import worker from '../../worker.js';
export const TEST_ADMIN_PASSWORD='local-test-admin-1234';
const root=fileURLToPath(new URL('../../',import.meta.url));
export function createDatabase(){
 const sqlite=new DatabaseSync(':memory:');sqlite.exec('PRAGMA foreign_keys=ON');
 for(const f of readdirSync(path.join(root,'migrations')).filter(x=>x.endsWith('.sql')).sort())sqlite.exec(readFileSync(path.join(root,'migrations',f),'utf8'));
 const db={prepare(query){let args=[];const s={bind(...a){args=a;return s},async first(){return sqlite.prepare(query).get(...args)||null},async all(){return {results:sqlite.prepare(query).all(...args)}},async run(){const r=sqlite.prepare(query).run(...args);return {meta:{changes:Number(r.changes)}}}};return s},async batch(statements){sqlite.exec('BEGIN');try{const result=[];for(const s of statements)result.push(await s.run());sqlite.exec('COMMIT');return result}catch(e){sqlite.exec('ROLLBACK');throw e}}};
 return {db,sqlite};
}
export async function startServer(port=0){
 const {db,sqlite}=createDatabase();
 const env={DB:db,ADMIN_PASSWORD:TEST_ADMIN_PASSWORD,ASSETS:{async fetch(req){let name=new URL(req.url).pathname;if(name==='/')name='/index.html';const allowed=['/index.html','/app.js','/style.css','/admin.html','/admin.js','/admin.css'];if(!allowed.includes(name))return new Response('Not found',{status:404});const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css'};return new Response(readFileSync(path.join(root,'static',name.slice(1))),{headers:{'Content-Type':mime[path.extname(name)]+'; charset=utf-8'}})}}};
 const server=createServer(async(req,res)=>{try{const buffers=[];for await(const c of req)buffers.push(c);const body=Buffer.concat(buffers);const request=new Request('http://127.0.0.1:'+server.address().port+req.url,{method:req.method,headers:req.headers,body:['GET','HEAD'].includes(req.method)?undefined:body});const r=await worker.fetch(request,env);res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()))}catch(e){console.error(e);res.writeHead(500);res.end('Test adapter error')}});
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve)});
 return {url:'http://127.0.0.1:'+server.address().port,sqlite,async close(){server.closeAllConnections();await new Promise(resolve=>server.close(resolve));sqlite.close()}};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const server=await startServer(8790);console.log('Isolated test server: '+server.url);
 for(const signal of ['SIGINT','SIGTERM'])process.on(signal,async()=>{await server.close();process.exit(0)});
}
