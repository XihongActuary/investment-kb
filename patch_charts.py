# -*- coding: utf-8 -*-
"""修补 4 张图：美林时钟象限、CPPI 地板、有效边界标注、久期凸度标注。"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

PAPER='#f5f1e6'; INK='#2b2a26'; RED='#b53d2e'; AMBER='#bb8a1f'; TEAL='#2f6b5a'; GRAY='#8a8578'
OUT='img/'

def style_ax(ax):
    ax.set_facecolor(PAPER)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['left','bottom']: ax.spines[s].set_color('#c9c4b6')
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(True, color='#e0dbcd', linewidth=0.8, alpha=0.7)

# ============ 1. 美林时钟（修正象限与轴） ============
def merrill_clock():
    fig, ax = plt.subplots(figsize=(6.4, 6.6), dpi=150)
    ax.set_facecolor(PAPER); ax.axis('off')
    theta = np.linspace(0, 2*np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color=INK, lw=2)
    ax.plot([-1.22,1.22],[0,0], color='#c9c4b6', lw=1.2)
    ax.plot([0,0],[-1.22,1.22], color='#c9c4b6', lw=1.2)
    # 标准美林时钟（顺时针）：左上复苏 → 右上过热 → 右下滞胀 → 左下衰退
    quads = [
        ('复苏', '增长↑ 通胀↓', '利好：股票', TEAL, -0.46, 0.5),
        ('过热', '增长↑ 通胀↑', '利好：商品', AMBER, 0.46, 0.5),
        ('滞胀', '增长↓ 通胀↑', '利好：现金', RED, 0.46, -0.5),
        ('衰退', '增长↓ 通胀↓', '利好：债券', INK, -0.46, -0.5),
    ]
    for name, cond, asset, c, x, y in quads:
        ax.text(x, y+0.08, name, ha='center', va='center', fontsize=15, color=c, fontweight='bold')
        ax.text(x, y-0.14, cond, ha='center', va='center', fontsize=9.5, color=INK)
        ax.text(x, y-0.32, asset, ha='center', va='center', fontsize=10.5, color=c, fontweight='bold')
    # 顺时针箭头（12→3→6→9点方向）
    for ang0 in [70, 340, 250, 160]:
        a = np.linspace(np.deg2rad(ang0), np.deg2rad(ang0-55), 30)
        r = 1.12
        xs, ys = r*np.cos(a), r*np.sin(a)
        ax.plot(xs, ys, color=GRAY, lw=1.6)
        ax.annotate('', xy=(xs[-1], ys[-1]), xytext=(xs[-6], ys[-6]),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.6))
    ax.text(0, 1.34, '增长加速 ↑', ha='center', fontsize=10, color=GRAY)
    ax.text(0, -1.34, '增长放缓 ↓', ha='center', fontsize=10, color=GRAY)
    ax.text(1.36, 0, '通胀上升 →', va='center', fontsize=10, color=GRAY)
    ax.text(-1.36, 0, '← 通胀下降', va='center', fontsize=10, color=GRAY)
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.52, 1.52)
    ax.set_title('美林时钟：经济周期与资产轮动（顺时针）', fontsize=12, color=INK, pad=10)
    fig.savefig(OUT+'merrill-clock.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig); print('OK merrill-clock v2')

# ============ 2. CPPI（修正下跌端地板） ============
def cppi():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    style_ax(ax)
    mkt = np.linspace(-30, 30, 300)
    bh   = mkt                                   # 购买持有：线性
    cm   = 0.85*mkt - 0.006*mkt**2               # 恒定组合：凹
    cppi = 6*np.expm1(mkt/22)                    # CPPI：凸 + 下跌端地板
    ax.plot(mkt, bh, color=INK, lw=2.2, label='购买并持有（线性）')
    ax.plot(mkt, cm, color=AMBER, lw=2.2, label='恒定组合（凹型）')
    ax.plot(mkt, cppi, color=RED, lw=2.4, label='CPPI / 组合保险（凸型）')
    ax.axhline(-9, color=RED, lw=1, ls=':', alpha=0.7)
    ax.annotate('保本「地板」：跌破即止损减仓，\n组合价值趋近保本线', (-29, -8.4),
                textcoords='offset points', xytext=(4, 8), color=RED, fontsize=8.5, fontweight='bold')
    ax.annotate('凹型：单边大涨大跌都跑输，\n震荡市高抛低吸占优', (22, 14),
                textcoords='offset points', xytext=(-96, -26), color=AMBER, fontsize=8.5, fontweight='bold')
    ax.annotate('凸型：跌了卖（止损）、涨了买（追涨）', (10, 5.4),
                textcoords='offset points', xytext=(6, 14), color=RED, fontsize=8.5)
    ax.axhline(0, color='#c9c4b6', lw=1); ax.axvline(0, color='#c9c4b6', lw=1)
    ax.set_xlabel('市场涨跌幅（%）', fontsize=10)
    ax.set_ylabel('组合价值变化（%）', fontsize=10)
    ax.set_xlim(-30, 30); ax.set_ylim(-32, 32)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.85)
    ax.set_title('三种策略的支付曲线：CPPI 凸（有地板）、恒定组合凹', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'cppi.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig); print('OK cppi v2')

# ============ 3. 有效边界（修标注重叠） ============
def eff_frontier():
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    style_ax(ax)
    sigma = np.linspace(6, 30, 200)
    E = 4 + 0.28*sigma + 0.0035*sigma**2
    ax.fill_between(sigma, E, 2 + 0.12*sigma, color=TEAL, alpha=0.08)
    ax.plot(sigma, E, color=INK, lw=2.4, label='有效边界（上半支）')
    g_s, g_e = 6, 4 + 0.28*6 + 0.0035*36
    ax.scatter([g_s],[g_e], color=AMBER, s=60, zorder=5)
    ax.annotate('最小方差组合 G', (g_s, g_e), textcoords='offset points', xytext=(-6, -22), color=AMBER, fontsize=9, ha='center')
    rf = 3
    ax.scatter([0],[rf], color=AMBER, s=60, zorder=5)
    ax.annotate('无风险资产 r$_f$', (0, rf), textcoords='offset points', xytext=(6, -14), color=AMBER, fontsize=9)
    tang_sigma = 15.5
    tang_E = 4 + 0.28*tang_sigma + 0.0035*tang_sigma**2
    slope = (tang_E - rf)/tang_sigma
    cml_y = rf + slope*np.linspace(0, 30, 100)
    ax.plot(np.linspace(0, 30, 100), cml_y, color=RED, lw=2, ls='--', label='资本市场线 CML')
    ax.scatter([tang_sigma],[tang_E], color=RED, s=80, zorder=5)
    ax.annotate('切点组合 M（市场组合）', (tang_sigma, tang_E), textcoords='offset points', xytext=(-10, 16), color=RED, fontsize=9, fontweight='bold', ha='right')
    # 无差异曲线：凸向原点，放在右上方区域（不与 CML 交叠）
    for U, c in [(15.5, GRAY), (19.5, GRAY)]:
        ux = np.linspace(10, 29.5, 120)
        uy = U - 0.010*(ux-10)**2 + 0.9
        uy = np.clip(uy, None, 25.5)
        ax.plot(ux, uy, color=GRAY, lw=1.2, ls=':', alpha=0.85)
    ax.annotate('无差异曲线（凸向原点，\n风险厌恶者）', (29.3, 15.2), textcoords='offset points',
                xytext=(-2, -30), color=GRAY, fontsize=8.5, ha='right')
    ax.set_xlabel('组合标准差 σ（总风险）', fontsize=10)
    ax.set_ylabel('期望收益 E(r) %', fontsize=10)
    ax.set_xlim(0, 30); ax.set_ylim(0, 26)
    ax.legend(loc='lower right', fontsize=8.5, framealpha=0.85)
    ax.set_title('有效边界、资本市场线 CML 与切点组合 M', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'eff-frontier.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig); print('OK eff-frontier v2')

# ============ 4. 久期凸度（修标注位置） ============
def duration_convexity():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    style_ax(ax)
    y = np.linspace(0.02, 0.14, 300)
    P = 100/(1+y)**10 + 6*(1-(1+y)**-10)/y
    ax.plot(y*100, P, color=INK, lw=2.6, label='真实价格-利率曲线（凸）')
    y0 = 0.08
    P0 = 100/(1+y0)**10 + 6*(1-(1+y0)**-10)/y0
    dy = 1e-5
    dPdy = (100/(1+y0+dy)**10 + 6*(1-(1+y0+dy)**-10)/(y0+dy) - P0)/dy   # 数值导数
    tan_y = P0 + dPdy*(y - y0)
    ax.plot(y*100, tan_y, color=RED, lw=2, ls='--', label='久期（切线）一阶近似')
    ax.scatter([8],[P0], color=AMBER, s=60, zorder=5)
    ax.annotate('切点 y=8%', (8, P0), textcoords='offset points', xytext=(10, -16), color=AMBER, fontsize=9, fontweight='bold')
    ax.annotate('利率下行的「多涨」\n（曲线高于切线）', (3.4, P[34]), textcoords='offset points',
                xytext=(-6, 30), color=TEAL, fontsize=8.5, fontweight='bold')
    ax.annotate('利率上行的「少跌」', (12.6, tan_y[224]), textcoords='offset points',
                xytext=(-70, 26), color=TEAL, fontsize=8.5, fontweight='bold')
    ax.annotate('', xy=(3.5, 133), xytext=(3.5, 124), arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.3))
    ax.annotate('', xy=(12.9, 61), xytext=(12.9, 54), arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.3))
    ax.set_xlabel('到期收益率 y（%）', fontsize=10)
    ax.set_ylabel('债券价格 P', fontsize=10)
    ax.set_xlim(2, 14); ax.set_ylim(40, 142)
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.85)
    ax.set_title('久期是「切线」，凸度是「弯曲」——凸度使价格涨多跌少', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'duration-convexity.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig); print('OK duration-convexity v2')

if __name__ == '__main__':
    merrill_clock(); cppi(); eff_frontier(); duration_convexity()
    print('PATCH DONE')
