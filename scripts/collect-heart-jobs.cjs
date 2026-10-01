const fs=require('fs'),cp=require('child_process'),crypto=require('crypto');
const command='npx.cmd --yes --package @playwright/cli playwright-cli -s=heart run-code --filename scripts/collect-heart-jobs.js';
const out=cp.execFileSync(process.env.ComSpec||'cmd.exe',['/d','/s','/c',command],{encoding:'utf8',maxBuffer:4*1024*1024});
const match=out.match(/### Result\r?\n([\s\S]*?)\r?\n###/);
if(!match)throw Error(out);
const data=JSON.parse(match[1]);
const jobs=data.texts.map(text=>({id:'heart-'+crypto.createHash('sha256').update(text).digest('hex').slice(0,20),text}));
fs.mkdirSync('output',{recursive:true});fs.writeFileSync('output/heart-jobs.json',JSON.stringify(jobs,null,2));
console.log(JSON.stringify({pages:data.pages,jobs:jobs.length,characters:jobs.reduce((n,j)=>n+j.text.length,0)}));
