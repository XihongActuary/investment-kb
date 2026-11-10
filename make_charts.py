# -*- coding: utf-8 -*-
"""投资学 F8 知识库技术图表生成器
统一水墨风五色配色，输出到 img/ 目录。
涨=红、跌=绿（中国股市惯例）。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

# 中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun']
plt.rcParams['axes.unicode_minus'] = False

# 水墨五色
PAPER = '#f5f1e6'   # 宣纸底
INK   = '#2b2a26'   # 墨
RED   = '#b53d2e'   # 朱砂（涨/正向/低估）
AMBER = '#bb8a1f'   # 琥珀
TEAL  = '#2f6b5a'   # 青绿（跌/负向/高估）
GRAY  = '#8a8578'   # 灰

OUT = 'img/'

def style_ax(ax):
    ax.set_facecolor(PAPER)
    for s in ['top','right']:
        ax.spines[s].set_visible(False)
    for s in ['left','bottom']:
        ax.spines[s].set_color('#c9c4b6')
    ax.tick_params(colors=INK, labelsize=9)
    ax.grid(True, color='#e0dbcd', linewidth=0.8, alpha=0.7)

# ============ 1. 有效边界 + CML + 无差异曲线 ============
def eff_frontier():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    style_ax(ax)
    # 两资产可行集（含ρ的几种情形示意）
    # 构造一个凹的可行集
    xs = np.linspace(0, 1, 200)
    # 用二次曲线近似有效边界
    sigma = np.linspace(6, 30, 200)
    E = 4 + 0.28*sigma + 0.0035*sigma**2   # 单调递增凹的边界
    ax.plot(sigma, E, color=INK, lw=2.4, label='有效边界（上半支）')
    # 可行集内部（填充感）
    ax.fill_between(sigma, E, 2 + 0.12*sigma, color=TEAL, alpha=0.08)
    # 最低风险组合（最小方差组合 G）
    g_s, g_e = 6, 4 + 0.28*6 + 0.0035*36
    ax.scatter([g_s],[g_e], color=AMBER, s=60, zorder=5)
    ax.annotate('最小方差组合 G', (g_s, g_e), textcoords='offset points', xytext=(10,-16), color=AMBER, fontsize=9)
    # 无风险资产 rf
    rf = 3
    ax.scatter([0],[rf], color=AMBER, s=60, zorder=5)
    ax.annotate('无风险资产 r$_f$', (0, rf), textcoords='offset points', xytext=(8,4), color=AMBER, fontsize=9)
    # CML 切点
    # 找到从 rf 到有效边界的切点（切线）
    tang_sigma, tang_E = 15.5, 4 + 0.28*15.5 + 0.0035*15.5**2
    cml_x = np.linspace(0, 30, 100)
    slope = (tang_E - rf)/tang_sigma
    cml_y = rf + slope*cml_x
    ax.plot(cml_x, cml_y, color=RED, lw=2, ls='--', label='资本市场线 CML')
    ax.scatter([tang_sigma],[tang_E], color=RED, s=80, zorder=5)
    ax.annotate('切点组合 M\n(市场组合)', (tang_sigma, tang_E), textcoords='offset points', xytext=(10,8), color=RED, fontsize=9, fontweight='bold')
    # 无差异曲线（两条示意）
    for U in [6.5, 8.5]:
        ux = np.linspace(8, 30, 100)
        uy = U + 0.012*(ux-14)**2
        ax.plot(ux, uy, color=GRAY, lw=1.2, ls=':', alpha=0.8)
    ax.annotate('无差异曲线\n(风险厌恶者)', (26, 8.5+0.012*144), textcoords='offset points', xytext=(-30,-2), color=GRAY, fontsize=8.5)
    ax.set_xlabel('组合标准差 σ（总风险）', fontsize=10)
    ax.set_ylabel('期望收益 E(r) %', fontsize=10)
    ax.set_xlim(0, 30); ax.set_ylim(0, 26)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.8)
    ax.set_title('有效边界、资本市场线 CML 与切点组合 M', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'eff-frontier.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK eff-frontier')

# ============ 2. SML 与高估/低估 ============
def sml():
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    style_ax(ax)
    beta = np.linspace(0, 2.2, 100)
    rf, rm = 3, 10
    sml_y = rf + beta*(rm-rf)
    ax.plot(beta, sml_y, color=INK, lw=2.4, label='证券市场线 SML：E(r)=r$_f$+β·MRP')
    ax.scatter([0],[rf], color=AMBER, s=60, zorder=5)
    ax.annotate('r$_f$=3%', (0, rf), textcoords='offset points', xytext=(8,-4), color=AMBER, fontsize=9)
    ax.scatter([1],[rm], color=INK, s=60, zorder=5)
    ax.annotate('市场组合 M\n(β=1, E=10%)', (1, rm), textcoords='offset points', xytext=(10,6), color=INK, fontsize=9)
    # 低估点（SML上方）
    ax.scatter([1.2],[12.6], color=RED, s=70, zorder=5)
    ax.annotate('低估（SML 上方）\nα>0，买入', (1.2,12.6), textcoords='offset points', xytext=(8,6), color=RED, fontsize=9, fontweight='bold')
    # 高估点（SML下方）
    ax.scatter([1.5],[11.5], color=TEAL, s=70, zorder=5)
    ax.annotate('高估（SML 下方）\nα<0，卖出', (1.5,11.5), textcoords='offset points', xytext=(8,-22), color=TEAL, fontsize=9, fontweight='bold')
    ax.set_xlabel('β（系统风险）', fontsize=10)
    ax.set_ylabel('期望收益 E(r) %', fontsize=10)
    ax.set_xlim(0, 2.2); ax.set_ylim(0, 20)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.8)
    ax.set_title('证券市场线 SML：横轴是 β，不是 σ', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'sml.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK sml')

# ============ 3. 久期（切线）vs 凸度（曲线） ============
def duration_convexity():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    style_ax(ax)
    y = np.linspace(0.02, 0.14, 200)   # 利率 2%~14%
    # 真实价格-利率曲线（凸函数）
    P = 100/(1+y)**10 + 6*(1-(1+y)**-10)/y   # 10年期 票面6% 债券近似
    ax.plot(y*100, P, color=INK, lw=2.6, label='真实价格-利率曲线（凸）')
    # 在 y=8% 处做切线（久期近似）
    y0 = 0.08
    P0 = 100/(1+y0)**10 + 6*(1-(1+y0)**-10)/y0
    # 切线斜率 = -D_mod * P0，近似 D_mod≈7.5
    Dmod = 7.5
    slope = -Dmod*P0/100
    tan_y = P0 + slope*(y*100 - 8)
    ax.plot(y*100, tan_y, color=RED, lw=2, ls='--', label='久期（切线）近似')
    ax.scatter([8],[P0], color=AMBER, s=60, zorder=5)
    # 标注凸度贡献
    ax.annotate('凸度贡献：\n涨多跌少', (6.3, tan_y[63]), textcoords='offset points', xytext=(-10,-34), color=TEAL, fontsize=9, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.2))
    ax.annotate('在 y=8% 处\n久期只给切线', (8, P0), textcoords='offset points', xytext=(14,-4), color=RED, fontsize=9)
    ax.set_xlabel('到期收益率 y（%）', fontsize=10)
    ax.set_ylabel('债券价格 P', fontsize=10)
    ax.set_xlim(2, 14)
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.8)
    ax.set_title('久期是「切线」，凸度是「弯曲」——凸度使价格涨多跌少', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'duration-convexity.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK duration-convexity')

# ============ 4. 收益率曲线四种形态 ============
def yield_curve():
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.4), dpi=150)
    maturities = [1,2,3,5,7,10,20,30]
    curves = {
        '向上倾斜（正常）': [2.2,2.6,2.9,3.2,3.4,3.6,3.9,4.1],
        '向下倾斜（倒挂）': [4.1,3.8,3.5,3.1,2.9,2.7,2.5,2.4],
        '平坦': [3.0,3.0,3.0,3.0,3.0,3.0,3.0,3.0],
        '驼峰（先升后降）': [2.5,2.9,3.2,3.4,3.5,3.4,3.2,3.0],
    }
    colors = [TEAL, RED, AMBER, INK]
    for ax, (name, vals), c in zip(axes, curves.items(), colors):
        style_ax(ax)
        ax.plot(maturities, vals, color=c, lw=2.4, marker='o', markersize=4)
        ax.set_title(name, fontsize=10, color=INK)
        ax.set_xlabel('期限(年)', fontsize=8)
        ax.set_ylabel('收益率%', fontsize=8)
        ax.set_ylim(1.8, 4.6)
        ax.tick_params(labelsize=7)
    fig.suptitle('利率期限结构的四种形态（倒挂常是衰退领先指标）', fontsize=12, color=INK, y=1.04)
    fig.tight_layout()
    fig.savefig(OUT+'yield-curve.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK yield-curve')

# ============ 5. 美林时钟 ============
def merrill_clock():
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=150)
    ax.set_facecolor(PAPER)
    ax.axis('off')
    # 画圆
    theta = np.linspace(0, 2*np.pi, 400)
    ax.plot(np.cos(theta), np.sin(theta), color=INK, lw=2)
    # 四象限分割线
    ax.plot([-1.25,1.25],[0,0], color='#c9c4b6', lw=1.2)
    ax.plot([0,0],[-1.25,1.25], color='#c9c4b6', lw=1.2)
    # 四个象限
    quads = [
        ('复苏（Recovery）', '增长↑ 通胀↓', '股票', RED, 0.45, 0.45, 45),
        ('过热（Overheat）', '增长↑ 通胀↑', '商品', AMBER, -0.45, 0.45, 315),
        ('滞胀（Stagflation）', '增长↓ 通胀↑', '现金', TEAL, -0.45, -0.45, 225),
        ('衰退（Recession）', '增长↓ 通胀↓', '债券', INK, 0.45, -0.45, 135),
    ]
    for name, cond, asset, c, x, y, ang in quads:
        ax.text(x, y, f'{name}\n{cond}\n\n利好：{asset}', ha='center', va='center', fontsize=11, color=c, fontweight='bold')
    # 循环箭头
    for ang in [0, 90, 180, 270]:
        a = np.deg2rad(ang)
        ax.annotate('', xy=(np.cos(a)*1.18, np.sin(a)*1.18), xytext=(np.cos(a)*0.92, np.sin(a)*0.92),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.6, connectionstyle='arc3,rad=0.25'))
    # 轴标签
    ax.text(0, 1.32, '通胀上升', ha='center', fontsize=9, color=GRAY)
    ax.text(0, -1.32, '通胀下降', ha='center', fontsize=9, color=GRAY)
    ax.text(1.32, 0, '增长加速', va='center', fontsize=9, color=GRAY)
    ax.text(-1.32, 0, '增长放缓', va='center', fontsize=9, color=GRAY)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.set_title('美林时钟：经济周期与资产配置', fontsize=12, color=INK, pad=8)
    fig.savefig(OUT+'merrill-clock.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK merrill-clock')

# ============ 6. CPPI vs 恒定组合 支付曲线 ============
def cppi():
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=150)
    style_ax(ax)
    mkt = np.linspace(-30, 30, 200)  # 市场涨跌幅%
    # 购买持有：线性
    bh = mkt
    # 恒定组合：凹型（涨了卖跌了买，震荡市占优）
    const = 0.85*mkt - 0.006*mkt**2
    # CPPI：凸型（跌了卖涨了买）
    cppi = 0.7*mkt + 0.009*mkt**2
    ax.plot(mkt, bh, color=INK, lw=2.2, label='购买并持有（线性）')
    ax.plot(mkt, const, color=AMBER, lw=2.2, label='恒定组合（凹型，高抛低吸）')
    ax.plot(mkt, cppi, color=RED, lw=2.2, label='CPPI（凸型，顺势止损/加仓）')
    ax.axhline(0, color='#c9c4b6', lw=1)
    ax.axvline(0, color='#c9c4b6', lw=1)
    ax.set_xlabel('市场涨跌幅（%）', fontsize=10)
    ax.set_ylabel('组合价值变化（%）', fontsize=10)
    ax.set_xlim(-30, 30)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.8)
    ax.set_title('三种策略的支付曲线形状：CPPI 凸、恒定组合凹', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'cppi.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK cppi')

# ============ 7. 两期二叉树 ============
def binomial():
    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=150)
    ax.set_facecolor(PAPER); ax.axis('off')
    S0 = 50
    u, d = 1.2, 0.8
    nodes = {0:[(0,0,S0)], 1:[(-0.5,1,S0*u),(0.5,1,S0*d)], 2:[(-1,2,S0*u*u),(0,2,S0*u*d),(1,2,S0*d*d)]}
    # 连线
    for t in range(2):
        for (x,y,v) in nodes[t]:
            for (x2,y2,v2) in nodes[t+1]:
                if y2==y+1 and abs(x2-x)<0.51:
                    ax.plot([x,x2],[y,y2], color=INK, lw=1.4, alpha=0.7)
    for t, lst in nodes.items():
        for (x,y,v) in lst:
            ax.scatter([x],[y], s=500, color='white', edgecolor=INK, linewidth=1.6, zorder=3)
            ax.text(x, y, f'{v:.0f}', ha='center', va='center', fontsize=11, color=INK, fontweight='bold', zorder=4)
    # p 标注
    ax.text(-0.12, 0.52, 'p', fontsize=11, color=RED, fontweight='bold')
    ax.text(0.18, 0.52, '1−p', fontsize=11, color=TEAL, fontweight='bold')
    ax.text(-0.55, 1.52, 'p', fontsize=11, color=RED, fontweight='bold')
    ax.text(-0.38, 1.52, '1−p', fontsize=11, color=TEAL, fontweight='bold')
    ax.set_xlim(-1.4, 1.4); ax.set_ylim(-0.4, 2.6)
    ax.set_title('两期二叉树（u=1.2, d=0.8, S₀=50）\n风险中性概率 p=(1+r−d)/(u−d)', fontsize=11, color=INK, pad=4)
    fig.savefig(OUT+'binomial.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK binomial')

# ============ 8. 资产风险收益特征 ============
def risk_return():
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    style_ax(ax)
    assets = [
        ('货币市场', 1.5, 8.5, TEAL),
        ('国债/金融债', 3.0, 6.0, TEAL),
        ('高等级信用债', 3.5, 7.5, TEAL),
        ('高股息蓝筹', 5.5, 8.0, RED),
        ('股票型基金', 7.5, 18.0, RED),
        ('未上市股权', 9.0, 25.0, RED),
        ('不动产/基建', 7.0, 16.0, AMBER),
        ('对冲/另类', 6.0, 14.0, AMBER),
        ('大宗商品', 6.5, 20.0, GRAY),
    ]
    for name, ret, vol, c in assets:
        ax.scatter([vol], [ret], s=90, color=c, zorder=4, alpha=0.9)
        ax.annotate(name, (vol, ret), textcoords='offset points', xytext=(8,3), fontsize=9, color=c)
    # 一条「有效前沿」示意
    vx = np.linspace(0, 28, 100)
    ax.plot(vx, 1.2 + 0.32*vx - 0.002*vx**2, color=INK, lw=2, ls='--', alpha=0.6, label='示意有效前沿')
    ax.set_xlabel('风险（标准差 %）', fontsize=10)
    ax.set_ylabel('预期收益（%）', fontsize=10)
    ax.set_xlim(0, 30); ax.set_ylim(0, 12)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.8)
    ax.set_title('不同类别资产的风险-收益特征（险资配置地图）', fontsize=11, color=INK, pad=10)
    fig.tight_layout()
    fig.savefig(OUT+'risk-return.png', facecolor=PAPER, bbox_inches='tight')
    plt.close(fig)
    print('OK risk-return')

if __name__ == '__main__':
    eff_frontier()
    sml()
    duration_convexity()
    yield_curve()
    merrill_clock()
    cppi()
    binomial()
    risk_return()
    print('ALL DONE')
