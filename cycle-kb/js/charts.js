/* ============================================================
   四季 · 轻量 Canvas 图表库（无依赖）
   支持：折线/面积/柱状混合、区间底色、参考线、注释、象限时钟
   ============================================================ */
(function (w) {
  'use strict';

  var C = {
    ink: '#23241f', ink2: '#55564c', ink3: '#8a8b7e',
    line: '#e2dbc8', line2: '#cfc6ae', paper: '#fffdf7',
    spring: '#4a7c59', summer: '#b53d2e', autumn: '#bb8a1f',
    winter: '#3f5f7a', violet: '#534ab7'
  };
  w.CC = C;

  function font(px, weight, serif) {
    return (weight || 400) + ' ' + px + 'px ' + (serif
      ? '"Noto Serif SC","Songti SC",STSong,serif'
      : '"PingFang SC","Microsoft YaHei","Hiragino Sans GB",-apple-system,sans-serif');
  }

  function prepare(cv) {
    var dpr = w.devicePixelRatio || 1;
    var cw = cv.clientWidth || cv.parentNode.clientWidth || 640;
    var ch = cv.clientHeight || 320;
    if (cv.width !== Math.round(cw * dpr) || cv.height !== Math.round(ch * dpr)) {
      cv.width = Math.round(cw * dpr);
      cv.height = Math.round(ch * dpr);
    }
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cw, ch);
    return { ctx: ctx, W: cw, H: ch };
  }

  function niceTicks(min, max, n) {
    if (min === max) { max = min + 1; }
    var span = max - min;
    var step = Math.pow(10, Math.floor(Math.log(span / n) / Math.LN10));
    var err = span / n / step;
    if (err >= 7.5) step *= 10; else if (err >= 3.5) step *= 5; else if (err >= 1.5) step *= 2;
    var lo = Math.floor(min / step) * step, hi = Math.ceil(max / step) * step, out = [];
    for (var v = lo; v <= hi + step * 1e-6; v += step) out.push(Math.round(v * 1e6) / 1e6);
    return { ticks: out, lo: lo, hi: hi };
  }

  function fmtNum(v, dec) {
    if (dec === undefined) dec = Math.abs(v) >= 100 ? 0 : (Math.abs(v) >= 10 ? 1 : 2);
    return v.toFixed(dec).replace(/\.0+$/, '').replace(/(\.\d)0$/, '$1');
  }

  /* ---------------- 主轴图表 ---------------- */
  function axisChart(cv, cfg) {
    var draw = function () {
      var p = prepare(cv), ctx = p.ctx, W = p.W, H = p.H;
      var padL = cfg.padL || 46, padR = cfg.padR || 14, padT = cfg.padT || 16, padB = cfg.padB || 34;
      var labels = cfg.labels || [];
      var series = cfg.series || [];
      var n = labels.length;
      var iw = W - padL - padR, ih = H - padT - padB;
      if (n < 2 || iw <= 10 || ih <= 10) return;

      // 值域
      var vals = [];
      series.forEach(function (s) {
        if (s.axis === 'right' || s.hidden) return;
        s.data.forEach(function (v) { if (v !== null && v !== undefined && isFinite(v)) vals.push(v); });
      });
      if (cfg.bands) cfg.bands.forEach(function (b) { vals.push(b.to); });
      if (cfg.hlines) cfg.hlines.forEach(function (l) { vals.push(l.y); });
      var vmin = cfg.yMin !== undefined ? cfg.yMin : Math.min.apply(null, vals);
      var vmax = cfg.yMax !== undefined ? cfg.yMax : Math.max.apply(null, vals);
      if (vmin === vmax) { vmin -= 1; vmax += 1; }
      var pad = (vmax - vmin) * 0.08;
      var tk = niceTicks(cfg.yMin !== undefined ? vmin : vmin - pad, cfg.yMax !== undefined ? vmax : vmax + pad, cfg.yTicks || 5);
      var lo = tk.lo, hi = tk.hi;

      var x = function (i) { return padL + iw * (i / (n - 1)); };
      var y = function (v) { return padT + ih - ih * ((v - lo) / (hi - lo)); };

      // 区间底色（四季）
      if (cfg.bands) cfg.bands.forEach(function (b) {
        var y0 = y(Math.max(b.from, lo)), y1 = y(Math.min(b.to, hi));
        if (y1 < padT) y1 = padT; if (y0 > padT + ih) y0 = padT + ih;
        if (y0 <= y1) return;
        ctx.fillStyle = b.color;
        ctx.fillRect(padL, y1, iw, y0 - y1);
        if (b.label) {
          ctx.fillStyle = b.text || C.ink3;
          ctx.font = font(10.5, 500);
          ctx.textAlign = 'left';
          ctx.fillText(b.label, padL + 6, y1 + 13);
        }
      });

      // 网格
      ctx.strokeStyle = C.line; ctx.lineWidth = 1;
      ctx.font = font(10.5);
      ctx.fillStyle = C.ink3;
      ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      tk.ticks.forEach(function (t) {
        var yy = Math.round(y(t)) + 0.5;
        ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(padL + iw, yy); ctx.stroke();
        ctx.fillText((cfg.yFmt ? cfg.yFmt(t) : fmtNum(t)) + (cfg.yUnit || ''), padL - 7, yy);
      });

      // 零线加粗
      if (lo < 0 && hi > 0) {
        ctx.strokeStyle = C.line2; ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.moveTo(padL, y(0) + 0.5); ctx.lineTo(padL + iw, y(0) + 0.5); ctx.stroke();
      }

      // 参考线
      if (cfg.hlines) cfg.hlines.forEach(function (l) {
        var yy = Math.round(y(l.y)) + 0.5;
        ctx.setLineDash([5, 4]); ctx.strokeStyle = l.color || C.summer; ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(padL + iw, yy); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = l.color || C.summer; ctx.font = font(10.5, 600); ctx.textAlign = 'left';
        ctx.fillText(l.label, padL + 6, yy - 8);
      });

      // x 轴标签
      ctx.textAlign = 'center'; ctx.textBaseline = 'top'; ctx.fillStyle = C.ink3; ctx.font = font(10.5);
      var stepx = Math.ceil(n / (cfg.xTicks || 8));
      labels.forEach(function (lb, i) {
        if (i % stepx !== 0 && i !== n - 1) return;
        if (i === n - 1 && n - 1 - Math.floor((n - 1) / stepx) * stepx < stepx * 0.5) { /* 保留 */ }
        ctx.fillText(lb, x(i), padT + ih + 8);
      });

      // 柱状
      series.forEach(function (s) {
        if (s.type !== 'bar' || s.hidden) return;
        var bw = Math.max(3, (iw / n) * (s.barW || 0.55));
        s.data.forEach(function (v, i) {
          if (v === null || v === undefined || !isFinite(v)) return;
          ctx.fillStyle = s.color;
          var y0 = y(0), y1 = y(v);
          ctx.beginPath();
          var rx = x(i) - bw / 2;
          var top = Math.min(y0, y1), h = Math.abs(y1 - y0);
          var r = Math.min(3, bw / 2, h);
          if (ctx.roundRect) { ctx.roundRect(rx, top, bw, h, [r, r, 0, 0]); ctx.fill(); }
          else ctx.fillRect(rx, top, bw, h);
        });
      });

      // 折线 / 面积
      series.forEach(function (s) {
        if (s.type === 'bar' || s.hidden) return;
        var pts = [];
        s.data.forEach(function (v, i) { if (v !== null && v !== undefined && isFinite(v)) pts.push([x(i), y(v), v, i]); });
        if (!pts.length) return;

        if (s.area) {
          var g = ctx.createLinearGradient(0, padT, 0, padT + ih);
          g.addColorStop(0, s.color + '38'); g.addColorStop(1, s.color + '04');
          ctx.beginPath();
          ctx.moveTo(pts[0][0], y(Math.max(lo, 0)));
          pts.forEach(function (pt0) { ctx.lineTo(pt0[0], pt0[1]); });
          ctx.lineTo(pts[pts.length - 1][0], y(Math.max(lo, 0)));
          ctx.closePath(); ctx.fillStyle = g; ctx.fill();
        }

        ctx.strokeStyle = s.color;
        ctx.lineWidth = s.lw || 2.1;
        ctx.lineJoin = 'round'; ctx.lineCap = 'round';
        if (s.dash) ctx.setLineDash(s.dash); else ctx.setLineDash([]);
        ctx.beginPath();
        pts.forEach(function (pt0, k) { k ? ctx.lineTo(pt0[0], pt0[1]) : ctx.moveTo(pt0[0], pt0[1]); });
        ctx.stroke();
        ctx.setLineDash([]);

        if (s.dots) pts.forEach(function (pt0) {
          ctx.beginPath(); ctx.arc(pt0[0], pt0[1], s.dots === true ? 2.6 : s.dots, 0, 7);
          ctx.fillStyle = C.paper; ctx.fill();
          ctx.strokeStyle = s.color; ctx.lineWidth = 2; ctx.stroke();
        });

        // 末端数值
        if (s.endLabel) {
          var last = pts[pts.length - 1];
          ctx.fillStyle = s.color; ctx.font = font(12, 700); ctx.textAlign = 'left'; ctx.textBaseline = 'bottom';
          var tx = last[0] + 6;
          if (tx > padL + iw - 26) { ctx.textAlign = 'right'; tx = last[0] - 6; }
          ctx.fillText(s.endLabel, tx, last[1] - 4);
        }
      });

      // 注释点
      if (cfg.marks) cfg.marks.forEach(function (m) {
        if (m.i === undefined || m.i >= n) return;
        var mx = x(m.i), my = y(m.y), off = m.dy || -26;
        ctx.beginPath(); ctx.arc(mx, my, 4, 0, 7); ctx.fillStyle = m.color || C.summer; ctx.fill();
        ctx.strokeStyle = C.paper; ctx.lineWidth = 1.6; ctx.stroke();
        ctx.beginPath(); ctx.moveTo(mx, my); ctx.lineTo(mx, my + off + 6); ctx.strokeStyle = m.color || C.summer; ctx.lineWidth = 1; ctx.stroke();
        ctx.fillStyle = m.color || C.summer; ctx.font = font(11, 600); ctx.textAlign = 'center';
        ctx.textBaseline = off < 0 ? 'bottom' : 'top';
        ctx.fillText(m.text, Math.min(Math.max(mx, padL + 34), padL + iw - 34), my + off);
      });

      // 轴框
      ctx.strokeStyle = C.line2; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(padL + 0.5, padT); ctx.lineTo(padL + 0.5, padT + ih + 0.5); ctx.lineTo(padL + iw, padT + ih + 0.5); ctx.stroke();
    };
    cv.__draw = draw;
    draw();
    observe(cv);
  }

  /* ---------------- 象限时钟 ---------------- */
  function quadrant(cv, cfg) {
    var draw = function () {
      var p = prepare(cv), ctx = p.ctx, W = p.W, H = p.H;
      var padL = 48, padR = 22, padT = 22, padB = 40;
      var iw = W - padL - padR, ih = H - padT - padB;
      var cx = padL + iw / 2, cy = padT + ih / 2;
      var rng = cfg.range || 3;
      var X = function (v) { return cx + (v / rng) * (iw / 2); };
      var Y = function (v) { return cy - (v / rng) * (ih / 2); };

      // 四象限底色
      var q = [
        { x: cx, y: padT, w: iw / 2, h: ih / 2, c: 'rgba(181,61,46,.075)', t: '过热 · 夏', sub: '增长↑ 通胀↑' },
        { x: padL, y: padT, w: iw / 2, h: ih / 2, c: 'rgba(74,124,89,.085)', t: '复苏 · 春', sub: '增长↑ 通胀↓' },
        { x: padL, y: cy, w: iw / 2, h: ih / 2, c: 'rgba(63,95,122,.075)', t: '衰退 · 冬', sub: '增长↓ 通胀↓' },
        { x: cx, y: cy, w: iw / 2, h: ih / 2, c: 'rgba(187,138,31,.09)', t: '滞胀 · 秋', sub: '增长↓ 通胀↑' }
      ];
      q.forEach(function (a) {
        ctx.fillStyle = a.c; ctx.fillRect(a.x, a.y, a.w, a.h);
        var align = a.x === padL ? 'left' : 'right';
        var tx = a.x === padL ? a.x + 14 : a.x + a.w - 14;
        var ty = a.y === padT ? a.y + 22 : a.y + a.h - 30;
        ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
        ctx.fillStyle = 'rgba(35,36,31,.62)'; ctx.font = font(14, 700, true);
        ctx.fillText(a.t, tx, ty);
        ctx.fillStyle = 'rgba(35,36,31,.42)'; ctx.font = font(11);
        ctx.fillText(a.sub, tx, ty + 16);
      });

      // 网格
      ctx.strokeStyle = 'rgba(35,36,31,.1)'; ctx.lineWidth = 1;
      for (var i = -3; i <= 3; i++) {
        if (i === 0) continue;
        ctx.beginPath(); ctx.moveTo(X(i), padT); ctx.lineTo(X(i), padT + ih); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(padL, Y(i)); ctx.lineTo(padL + iw, Y(i)); ctx.stroke();
      }
      // 轴
      ctx.strokeStyle = 'rgba(35,36,31,.42)'; ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.moveTo(padL, cy + .5); ctx.lineTo(padL + iw, cy + .5); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx + .5, padT); ctx.lineTo(cx + .5, padT + ih); ctx.stroke();

      // 轴名
      ctx.fillStyle = C.ink2; ctx.font = font(11.5, 600);
      ctx.textAlign = 'left'; ctx.textBaseline = 'top';
      ctx.fillText('通胀 / 价格动能 →', padL + iw - 116, cy + 6);
      ctx.save(); ctx.translate(padL - 14, padT + 4); ctx.rotate(-Math.PI / 2);
      ctx.textAlign = 'right'; ctx.textBaseline = 'top';
      ctx.fillText('增长动能 →', 0, 0); ctx.restore();

      // 轨迹
      if (cfg.trail && cfg.trail.length > 1) {
        ctx.strokeStyle = 'rgba(35,36,31,.28)'; ctx.lineWidth = 1.5; ctx.setLineDash([3, 3]);
        ctx.beginPath();
        cfg.trail.forEach(function (t, k) { k ? ctx.lineTo(X(t[0]), Y(t[1])) : ctx.moveTo(X(t[0]), Y(t[1])); });
        ctx.stroke(); ctx.setLineDash([]);
        cfg.trail.slice(0, -1).forEach(function (t) {
          ctx.beginPath(); ctx.arc(X(t[0]), Y(t[1]), 2.6, 0, 7); ctx.fillStyle = 'rgba(35,36,31,.22)'; ctx.fill();
        });
      }

      // 参照点（历史情景）
      if (cfg.points) cfg.points.forEach(function (pt) {
        var qx = X(pt.x), qy = Y(pt.y);
        ctx.beginPath(); ctx.arc(qx, qy, 3.6, 0, 7);
        ctx.fillStyle = 'rgba(35,36,31,.32)'; ctx.fill();
        ctx.strokeStyle = 'rgba(255,253,247,.9)'; ctx.lineWidth = 1.2; ctx.stroke();
        if (pt.label) {
          ctx.fillStyle = 'rgba(35,36,31,.42)'; ctx.font = font(9.5);
          ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
          ctx.fillText(pt.label, qx, qy - 6);
        }
      });

      // 当前点
      var px = X(cfg.x), py = Y(cfg.y);
      ctx.beginPath(); ctx.arc(px, py, 17, 0, 7); ctx.fillStyle = cfg.color + '22'; ctx.fill();
      ctx.beginPath(); ctx.arc(px, py, 8.5, 0, 7); ctx.fillStyle = cfg.color; ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.4; ctx.stroke();

      // 标签
      if (cfg.label) {
        ctx.font = font(12, 700); ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
        var lx = px + 16, ly = py - 14;
        var tw = ctx.measureText(cfg.label).width;
        if (lx + tw > W - 8) { lx = px - 16 - tw; }
        ctx.fillStyle = 'rgba(255,253,247,.92)';
        ctx.beginPath();
        if (ctx.roundRect) { ctx.roundRect(lx - 5, ly - 10, tw + 10, 20, 5); ctx.fill(); }
        else ctx.fillRect(lx - 5, ly - 10, tw + 10, 20);
        ctx.fillStyle = cfg.color; ctx.fillText(cfg.label, lx, ly);
      }
    };
    cv.__draw = draw;
    draw();
    observe(cv);
  }

  /* ---------------- 横条排行 ---------------- */
  function hbars(cv, cfg) {
    var draw = function () {
      var p = prepare(cv), ctx = p.ctx, W = p.W, H = p.H;
      var items = cfg.items || [];
      var padL = cfg.padL || 96, padR = 46, padT = 8, padB = 8;
      var iw = W - padL - padR, ih = H - padT - padB;
      var bh = ih / items.length;
      var mx = Math.max.apply(null, items.map(function (a) { return Math.abs(a.v); }));
      var zero = cfg.neg ? padL + iw / 2 : padL;
      var scale = cfg.neg ? (iw / 2) / mx : iw / mx;

      ctx.strokeStyle = C.line2; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(zero + .5, padT); ctx.lineTo(zero + .5, padT + ih); ctx.stroke();

      items.forEach(function (a, i) {
        var y0 = padT + i * bh + bh * 0.18, h = bh * 0.64;
        var len = Math.abs(a.v) * scale;
        var xx = a.v >= 0 ? zero : zero - len;
        ctx.fillStyle = a.color || (a.v >= 0 ? C.spring : C.summer);
        ctx.beginPath();
        if (ctx.roundRect) { ctx.roundRect(xx, y0, Math.max(len, 1.5), h, 3); ctx.fill(); }
        else ctx.fillRect(xx, y0, Math.max(len, 1.5), h);

        ctx.fillStyle = C.ink2; ctx.font = font(11.5); ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
        ctx.fillText(a.k, padL - 8, y0 + h / 2);
        ctx.fillStyle = a.color || C.ink2; ctx.font = font(11.5, 600);
        ctx.textAlign = a.v >= 0 ? 'left' : 'right';
        ctx.fillText(a.lb, (a.v >= 0 ? xx + len + 6 : xx - 6), y0 + h / 2);
      });
    };
    cv.__draw = draw;
    draw();
    observe(cv);
  }

  /* ---------------- 缩放重绘 ---------------- */
  var ro = null;
  function observe(cv) {
    if (!w.ResizeObserver) { w.addEventListener('resize', function () { if (cv.__draw) cv.__draw(); }); return; }
    if (!ro) {
      ro = new ResizeObserver(function (es) {
        es.forEach(function (e) { if (e.target.__draw) e.target.__draw(); });
      });
    }
    if (!cv.__observed) { ro.observe(cv); cv.__observed = true; }
  }

  w.Chart = { line: axisChart, axis: axisChart, quad: quadrant, hbars: hbars, prepare: prepare, font: font, fmtNum: fmtNum };
})(window);
