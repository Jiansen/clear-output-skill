const siteCopy={
 en:{headline:'Make AI answers easier<br>to understand and check.',summary:'Compare choices. Turn notes into action. Understand a process. Clear Output helps your agent choose useful words, diagrams, and interaction while preserving meaning and your chosen language.',installNav:'Install',explore:'Explore the examples ↓',installCta:'Install the skill',note:'English + 中文 · MIT licensed · No extra API key or background service',gallery:'Six ways to make the same information clearer',next:'TRY IT ON YOUR NEXT QUESTION',installTitle:'One skill. Your agent. Your language.',copyInstall:'Copy install command',installHelp:'Requires Node.js 22.20+. Run in your project and choose your agent. The installer asks where to place the skill. If you already installed it another way, use that copy.',manual:'Manual install, global install, and release ZIP →',chooseAgent:'Choose your agent for a sample prompt',copyPrompt:'Copy sample prompt',telemetry:'The optional skills CLI has its own installation telemetry. Set DISABLE_TELEMETRY=1 to opt out. Clear Output\'s instructions do not require it.',cliDocs:'Installer documentation',release:'Latest release',feedback:'Share a real example',copied:'Copied.',fallback:'Copy was unavailable. Select and copy the text above.',prompt:'Turn these meeting notes into a clear explanation. Preserve the decision, owners, deadline, dependency, and open question.\n\nThe team agreed to hold a workshop on Friday. Maya will confirm the room by Tuesday. Leo will send invitations after the room is confirmed. The budget is still undecided.'},
 zh:{headline:'让 AI 回答更清楚。<br>看懂它，核对它。',summary:'比较方案，整理行动项，看懂一个流程。Clear Output 帮助你的 agent 选择合适的文字、图示和交互，同时保留原意，以及你选择的语言。',installNav:'安装',explore:'查看六组示例 ↓',installCta:'安装技能',note:'中文 + English · MIT 开源 · 无需专用 API key 或后台服务',gallery:'六个例子：同样的信息，更清楚的表达',next:'用下一个问题试一试',installTitle:'同一个技能，你的 agent，你的语言。',copyInstall:'复制安装命令',installHelp:'需要 Node.js 22.20+。在项目目录运行并选择使用的 agent，安装器会询问安装位置。如果已经用其他方式安装，请继续使用已有副本。',manual:'手动安装、全局安装与正式版 ZIP →',chooseAgent:'选择 agent，复制一个示例提示词',copyPrompt:'复制示例提示词',telemetry:'可选的 skills CLI 有自己的安装遥测。设置 DISABLE_TELEMETRY=1 可以关闭；Clear Output 提示词本身不依赖它。',cliDocs:'安装器说明',release:'最新版本',feedback:'分享一个真实案例',copied:'已复制。',fallback:'复制功能不可用，请选中上方文字手动复制。',prompt:'把这些会议记录整理清楚。保留决定、负责人、截止时间、依赖条件和待定事项。\n\n团队决定周五举办工作坊。Maya 最晚周二确认场地；Leo 会在场地确认后发出邀请。预算仍未确定。'}
};
function updatePrompt(){
 const prefix=document.getElementById('prompt-agent').value==='codex'?'$clear-output':'/clear-output';
 document.getElementById('sample-prompt').textContent=prefix+' '+siteCopy[language].prompt;
}
function updateSite(){
 const copy=siteCopy[language];
 for(const element of document.querySelectorAll('[data-copy]')){
  if(element.dataset.copy==='headline') element.innerHTML=copy.headline;
  else element.textContent=copy[element.dataset.copy];
 }
 document.getElementById('page-title').textContent=copy.gallery;
 const link=document.getElementById('switch-language');
 link.href=language==='zh'?'?lang=en':'?lang=zh';link.textContent=language==='zh'?'English':'中文';
 document.getElementById('install-docs').href=language==='zh'?'https://github.com/Jiansen/clear-output-skill/blob/main/README.zh-CN.md#安装与使用':'https://github.com/Jiansen/clear-output-skill#install-and-use';
 document.getElementById('copy-status').textContent='';updatePrompt();
}
document.getElementById('language').addEventListener('change',()=>{
 const url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);updateSite();
});
document.getElementById('prompt-agent').addEventListener('change',updatePrompt);
for(const [button,target] of [['copy-install','install-command'],['copy-prompt','sample-prompt']]){
 document.getElementById(button).addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(document.getElementById(target).textContent);document.getElementById('copy-status').textContent=siteCopy[language].copied;}
  catch{document.getElementById('copy-status').textContent=siteCopy[language].fallback;}
 });
}
updateSite();
