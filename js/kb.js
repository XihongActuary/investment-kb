/* ============================================================
   中国精算师考试知识库 · 交互脚本（可复用骨架）
   功能：①学习进度记忆(localStorage) ②顶部滚动进度条 ③回到顶部
        ④模拟卷「展开/收起全部答案」 ⑤演算器框架
   新科目只需改 KEY 与 TOTAL，并在各页 data-id 处填唯一标识。
   ============================================================ */
(function(){
  'use strict';
  /* ====== 配置：每套库改这两处 ====== */
  var KEY  = 'INVEST-F8-KB-PROGRESS';     // localStorage 键名（唯一）
  var TOTAL = 13;                    // 计入进度的学习页总数（6章 + 6专题 + 真题馆 = 13；首页/说明/模拟卷/资料页不计入）
  var COUNTED = ['ch1','ch2','ch3','ch4','ch5','ch6',
                 'topic-term','topic-equity','topic-option','topic-perf','topic-alm','topic-topic',
                 'zhenti'];          // 仅这些 data-id 计入进度分母

  function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return{}}}
  function save(o){localStorage.setItem(KEY,JSON.stringify(o))}

  /* ---------- ① 学习进度记忆 ---------- */
  var p=load();
  document.querySelectorAll('.done-btn').forEach(function(b){
    var id=b.getAttribute('data-id');
    if(p[id]){b.classList.add('did');b.textContent='✓ 已完成（点击撤销）'}
    b.addEventListener('click',function(){
      p=load();
      if(p[id]){delete p[id];b.classList.remove('did');b.textContent='○ 标记本页已完成'}
      else{p[id]=Date.now();b.classList.add('did');b.textContent='✓ 已完成（点击撤销）'}
      save(p);renderMini();
    });
  });
  function renderMini(){
    var m=document.querySelector('.side .prog-mini b');
    if(m){var o=load();var n=0;COUNTED.forEach(function(id){if(o[id])n++});m.textContent=n+' / '+TOTAL}
  }
  renderMini();

  /* ---------- ② 顶部滚动进度条 ---------- */
  var bar=document.createElement('div');
  bar.style.cssText='position:fixed;top:0;left:0;height:3px;background:#EF9F27;z-index:99;transition:width .1s';
  document.body.appendChild(bar);

  /* ---------- ③ 回到顶部 ---------- */
  var top=document.createElement('button');
  top.className='back-top';top.textContent='↑';top.title='回到顶部';
  document.body.appendChild(top);
  top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});

  window.addEventListener('scroll',function(){
    var h=document.documentElement;
    var w=(h.scrollTop)/(h.scrollHeight-h.clientHeight)*100;
    bar.style.width=Math.min(100,Math.max(0,w))+'%';
    if(h.scrollTop>600){top.classList.add('show')}else{top.classList.remove('show')}
  });

  /* ---------- ④ 模拟卷：展开/收起全部答案 ---------- */
  document.querySelectorAll('.js-toggle-answers').forEach(function(btn){
    btn.addEventListener('click',function(){
      var boxes=document.querySelectorAll('details.answer');
      var anyClosed=false;
      boxes.forEach(function(d){if(!d.open)anyClosed=true});
      boxes.forEach(function(d){d.open=anyClosed});
      btn.textContent=anyClosed?'收起全部答案':'展开全部答案';
    });
  });

  /* ---------- ⑤ 演算器框架 ----------
     约定：每个演算器外层容器 class="calc"，内部输入含 class="calc-in"，
     输出容器含 class="verdict"，按钮含 class="calc-run"。
     交互原则：
     ① 初始不计算——输出区只显示占位提示，必须点击「计算」按钮才运行；
     ② run()（box.__run）由具体页面内联定义，输出应先列计算步骤（.calc-steps）再给结论；
     ③ 修改任一输入后，输出区提示「数据已修改，请重新点击计算」。 */
  document.querySelectorAll('.calc').forEach(function(box){
    function trigger(){
      if(typeof box.__run==='function'){ box.__did=true; box.__run(); }
    }
    var runBtn=box.querySelector('.calc-run');
    if(runBtn)runBtn.addEventListener('click',trigger);
    var vd=box.querySelector('.verdict');
    if(vd && !vd.innerHTML.trim()){
      vd.innerHTML='<span class="calc-hint">输入 / 调整数据后，点击「计算」按钮，查看分步计算过程与结论。</span>';
    }
    box.querySelectorAll('.calc-in').forEach(function(el){
      el.addEventListener('input',function(){
        if(vd && box.__did){vd.innerHTML='<span class="calc-hint">数据已修改，请重新点击「计算」按钮。</span>';}
      });
    });
  });
})();
