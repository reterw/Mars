import json,csv,html
from pathlib import Path
from collections import defaultdict
OUT=Path(__file__).resolve().parent
m=json.loads((OUT/'mars_model.json').read_text())
R=m['raw_materials'];P=m['products'];S=m['sources'];rec=m['recipes'];mat=m['materials']
def refs(ids):return '；'.join(f"[{i}]({S[i]['url']})" if S[i]['url'].startswith('http') else f'[{i}：设计假设]' for i in ids.split(';'))
def mdtable(headers,rows):
    esc=lambda x:str(x).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(esc(x) for x in row)+' |' for row in rows])
def tree_text(pid):
    seen={};lines=[];aliases=m.get('material_aliases',{})
    def canonical(id):
        while id in aliases:id=aliases[id]
        return id
    def visit(id,prefix='',last=True,root=False):
        marker='' if root else ('└─ ' if last else '├─ ')
        cid=canonical(id)
        if cid in seen:
            lines.append(prefix+marker+'↪ @'+seen[cid]+'（共享输入引用）');return
        did=pid if root else cid
        seen[cid]=did
        kind=mat[did]['kind'];mark={'raw':'[原料]','external':'[外部未闭合项]','terminal':'[终端]','intermediate':'[中间品]'}[kind]
        lines.append(prefix+marker+f'{did} {mat[did]["name"]} {mark}')
        kids=list(rec.get(cid,{}).get('inputs',{}))
        nextp=prefix+('' if root else ('   ' if last else '│  '))
        for j,k in enumerate(kids):visit(k,nextp,j==len(kids)-1)
    visit(pid,root=True)
    return '\n'.join(lines)
# separate process ledger, with output amounts independent of gross expansion
coids={'H2O':'M_W','H2':'M_H2','O2':'M_O2','CO2':'R02','gypsum':'A06','CO':'B_CO','HF':'B_HF','HCl':'B_HCl','SO2':'B_SO2','Cl2':'B_Cl2'}
with (OUT/'process_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['process_id','direction','material_id','amount','unit','basis','note'])
    for pid,r in rec.items():
        for k,v in r['inputs'].items():w.writerow([pid,'input',k,v,mat[k]['unit'],r['basis'],r['note']])
        w.writerow([pid,'primary_output',pid,1,r['unit'],r['basis'],'每次配方以1单位主产品归一化'])
        for k,v in r['coproducts'].items():w.writerow([pid,'coproduct',coids.get(k,k),v,'kg',r['basis'],'副产品必须按真实回收/合格率入库；不能与独立制备重复计数'])
forestparts={}
for name,slug in [('工业建设','industry'),('农业','agriculture'),('能源','energy')]:
    ps=[p for p in P if p['forest']==name]
    a=[f'# {name}产业链森林\n', '> 根是终端产品；原料以有效组分当量计。每棵树每种物质仅定义一次；↪ @ID是共享依赖引用，不另建物质节点。完整关系为有向无环投入图，不是不存在共享边的严格数学树。外部成套件不是火星自然资源；本版对这些分支诚实保留边界。\n']
    for p in ps:
        a += [f"## {p['id']} {p['name']}\n",f"单位：**{p['unit']}**。系数等级：**{p['basis']}**。规格：{p['spec']}。\n",'```text\n'+tree_text(p['id'])+'\n```\n',f"说明：{p['note'] or '主量物料模型；能耗/工时/设备能力另计。'}\n",f"依据：{refs(p['sources'])}。文献提供路线/现象依据，H系数由本模型设定。\n"]
    forestparts[name]='\n'.join(a)
    (OUT/f'forest_{slug}.md').write_text(forestparts[name],encoding='utf-8')
# Main report
lines=['# 火星工业—农业—能源生产底表 v0.1\n','核查日期：2026-10-03。适用范围：概念级系统动力学/工艺网络建模，**不是已验证的火星工厂工程设计**。\n',
'> 本版包含67项资源记录（含岩土化学指标、矿物、未证实矿藏和能量通量，并非67份独立矿体）、21种主原料当量、41种终端产品、69个选定配方和5类外部未闭合投入。\n',
'## 0. 先冻结口径\n',
'**检测到一种元素，不等于找到其矿床；存在资源，不等于知道储量；物料质量足够，也不等于能够造出满足性能要求的设备。** “所有自然物质”没有可验证的穷尽目录：本表覆盖与三类生产有关的已知主要物质类别，并显式保留未知。没有证据的矿床储量用未知/null，不伪造吨位、不默认无穷。\n',
'### 0.1 三种数值必须区分\n',
'- **观测丰度**：具体地点/样品或大气的质量/体积分数，必须保留空间和分析基准。\n- **资源库存估计**：例如区域冰的雷达体积解释；不是经济可采储量。\n- **设计系数 H**：为运行原型而设的品位、回收率、配方、成材率、设备质量与作物参数；不能引用NASA等机构为其背书。\n',
'系数标签：T=限定反应/纯物质条件下的化学计量；H=设计假设/占位BOM；U=依赖未证实矿藏。T也不是全流程能耗、损耗与杂质处理的实测值。\n',
'### 0.2 树结构约定\n',
'工业依赖具有共享输入。若要求根为成品、全部叶子是原料、全部投入边保留且每种物质仅一个节点，通常只能得到DAG，不能得到严格树。这里提供“唯一物质节点＋共享引用”的树形视图；JSON分别保存tree_edges和shared_edges。↪引用叶不是新增物质节点；无物料变化的终端命名转接已合并，不重复显示同一种净水、氢气等。计算以process_ledger.csv中的完整投入/产出关系为准，不能忽略引用。\n',
'### 0.3 原料单位与系统边界\n',
'主矩阵的行是**kg有效组分当量**，不是随手挖出的kg原矿。比如R07是Fe₂O₃当量，不意味着火星铁都作为纯Fe₂O₃存在；R14是铜矿的CuO当量计算代理，不是已证实天然氧化铜矿。原矿品位/选矿回收率另有情景换算表。多个元素若来自同一矿体，必须建立共享多产物采选过程，不能把分别计算的采矿量简单相加。\n',
'气体CO₂/N₂/Ar按成分质量列项；采集大气量需用质量分数及分离回收率计算。多个气体来自同一空气流时，进气需求取约束最大值，不机械相加。\n',
'外部电子件、精密件、特种辅材另成矩阵。这些不是火星天然资源；保留它们是指出链条未闭合，不能把本方案说成全自产。种子/种苗/菌种作为初始生物资本另设，不假定矿物会生成生命。\n',
'## 1. 火星自然资源与丰度/储量\n']
for group in dict.fromkeys(r['group'] for r in m['resources']):
    lines += ['### '+group+'\n',mdtable(['ID/对象','物质或当量','证据','丰度与基准','库存/体积估计','用途/说明','来源'],[[r['id']+' '+r['name'],r['formula'],r['status'],r['abundance'],r['inventory'],r['use']+'；'+r['note'],refs(r['sources'])] for r in m['resources'] if r['group']==group]),'\n']
lines += ['**共同储量字段：**本项目尚没有足以赋值的已探明经济可采储量。区域冰体积不能换成“可立即供城市使用的水”；局部氧化物百分数不能换成“整个火星同品位矿藏”。\n',
'## 2. 选定路线与终端产品\n',
'路线选择是以少引入稀有原料、优先电驱、常见化工/冶金工艺和可解释主计量为筛选原则，不声称在未知矿点、未知产量和能源价格下求得真正的最优路线。\n',
'建设优先风化层烧结；钢材采用氢还原铁加少量合成碳；透明板用富硅原料熔融路线，避免把混合玄武岩玻璃当透明压力窗；聚合物采用CO₂—H₂化工链。太阳能使用晶硅路线，明确跨越工业硅、太阳能级硅、电池和组件四个不同门槛。NiFe只是避免Li/Co原料的候选储能路线，仍依赖镍资源且需低温与维护验证。\n',
mdtable(['ID','模块','终端产品','一单位定义','系数','规格边界'],[[p['id'],p['forest'],p['name'],p['unit'],p['basis'],p['spec']] for p in P]),'\n',
'三个完整森林分别见forest_industry.md、forest_agriculture.md和forest_energy.md；本目录所有41个终端均有自己的树。\n',
'## 3. 原材料—终端产品矩阵\n',
'工作簿横轴为41个终端产品，纵轴为21个主原料。matrix_gross.csv与工作簿“主原料_毛投入”一致：\n',
'$$R^{gross}_{r,p}=\text{为独立生产1单位终端p，沿选定路线所需的原料r毛投入kg当量}.$$\n',
'末端p可以是kg产品、m²组件、套件或kWh名义储能容量；这些列不能不看单位就相加。\n',
'### 3.1 三张主矩阵的含义\n',
'1. **毛投入**：逐级展开选定配方。上游副产氧、水、石膏等另外列出，不在这一矩阵里偷偷抵扣。\n2. **理想回水**：仅把同一终端上游生成且可回收的水抵扣到R01；默认100%合格回收，仅作为上限情景，不是实际运行结果。其他副产品不抵扣。\n3. **矿料情景**：毛投入除以指定原料的假设品位g与回收率η。每行代表独立供料情景；不得当作真实探明采矿量或把共享矿体开挖量相加。\n',
'$$R^{mine}_{r,p}=R^{gross}_{r,p}/(g_r\eta_r).$$\n',
'实际生产调度必须基于单工艺投入/产出矩阵：\n',
'$$X_{t+1}=X_t+(B-A)u_t+imports_t-demand_t-losses_t,$$\n',
'其中u是工艺运行次数，A/B分别保留输入/主产品/副产品，不以“终端粗矩阵×总订单”取代联产调度。已从E06上游电解拿到氧气时，不要再次全额运行E08来生产同一份氧气。\n',
'### 3.2 示范子矩阵\n']
sel=['I01','I04','I05','A02','A03','E06','E07','E08','E01']
sp=[next(p for p in P if p['id']==x) for x in sel]
active=[r for r in R if any(p['gross_raw'].get(r['id'],0)>0 for p in sp)]
lines += [mdtable(['原料 kg当量']+[p['id']+' / '+p['unit'] for p in sp],[[r['id']+' '+r['name']]+[f"{p['gross_raw'].get(r['id'],0):.6g}" for p in sp] for r in active]),'\n',
'“0”只表示所选且已量化主路径没有该直接/间接输入；**不表示真实全产业链绝不需要该物质**。尤其R19萤石在主矩阵可能为0，而铝电解/光伏化工的辅材链尚未量化，必须同时查看未闭合项。\n',
'### 3.3 甲烷：毛水与净水为什么不同\n',
'$$CO_2+4H_2\\rightarrow CH_4+2H_2O.$$\n',
'上游电解供应氢，1kg甲烷的毛投入为约2.743kg CO₂、4.492kg水；Sabatier生成约2.246kg回水，上游联产约3.989kg氧气。完全回收内部水时，新增水降为约2.246kg，而不是4.492kg。设备启动水、压缩冷却、泄漏和合格率另计。\n',
'### 3.4 太阳能板与发电是两张账\n',
'本例E01是制造1m²晶硅组件：双玻8.8kg、铝框1kg、铜0.12kg、锡0.01kg、PDMS0.6kg、电池片组1组以及电子辅件；电池片进一步需要硅、银、铝、铜和掺杂/制程辅材。所有质量为H示例，不是经过验证的火星最佳组件。\n',
'硅片质量由2330kg/m³×180µm×0.9m²=0.37746kg推算；切片收得率设65%，太阳能级纯化收得率设90%。地表逐时发电则为\n',
'$$E_{PV}=\int A_{PV}\,G_{POA}(t)\,\eta_{module}(t)\,f_{dust}(t)\,dt.$$\n',
'这里G_POA必须是到达板面的辐照度；若其已包含大气尘暴衰减，就不要再次在f_dust里扣同一影响，f_dust可仅表示积尘。制造板的物料矩阵不把太阳光计为kg原料。\n',
'### 3.5 农业系数不能冒充化学定额\n',
'作物统一按kg可食干物质计，避免鲜重含水差异混淆。四类作物的收获指数、元素组成、蒸腾及回收率均为H占位；没有把NASA地面实验说成火星实测。用这些列可测试库存/需求接口，但不能作为精确农艺、生命支持定额。盐配方可能过供钙/硫，必须用离子平衡、pH、作物阶段和实测吸收修正。\n',
'CO₂既可能来自新采集，也可能来自呼吸/工业回收；循环水、库存补水和净化处理量要分别记录。温室、光照、温控、劳动、生长周期与种源是必需约束，不能因未摊入每kg原料矩阵而消失。\n',
'## 4. 未闭合项与模型使用闸门\n',
mdtable(['适用范围','问题','处理'],m['gaps']),'\n',
'**建议的可生产判定：**所需原料有库存且对应矿藏/进口已解锁，能源/设备/工时足够，所有不可替代外部输入有货，产品质量资格满足需求，才允许生产；否则给出明确阻塞原因。\n',
'## 5. 核查结果\n',
'已经自动检查：41棵树的物质节点定义无重复；配方依赖无递归环；主矩阵系数非负且有限；水电解、Sabatier、铁还原、硅还原、磷灰石酸解、CO₂电解六个反应按原子量核算质量守恒。\n',
'这些检查**没有证明**全部化学工艺可在火星运作、作物列完整守恒、设备性能满足名义标签，或所有能耗已闭合。\n',
'## 6. 文件说明\n',
'- mars_production_v01.xlsx：资源表、原料、终端规格、输入配方、过程产出、毛投入/回水/矿料/外部矩阵、假设和缺口。\n- mars_model.json：模型主数据与每棵树的唯一节点、树边和共享边。\n- process_ledger.csv：工艺级输入/主输出/副输出，适合编写守恒调度器。\n- matrix_*.csv：矩阵数值快照；修改参数后应从工作簿或程序重新导出，静态CSV不会自行更新。\n- build_model.py：生成主数据的标准库Python脚本；文件输出目录在文件开头指定。\n',
'## 7. 来源\n']
for k,v in S.items():lines.append(f"**{k}** {v['title']}。{v['note']}\n\n{v['url']}\n")
report='\n'.join(lines)
(OUT/'火星生产仿真_资源产业链与矩阵说明.md').write_text(report,encoding='utf-8')
# Lightweight searchable HTML of forests, not a generated image.
blocks=[]
for name in ['工业建设','农业','能源']:
    blocks.append(f'<h2>{name}</h2>')
    for p in [p for p in P if p['forest']==name]:
        blocks.append(f'<details><summary>{p["id"]} {html.escape(p["name"])} — {html.escape(p["unit"])}</summary><p>{html.escape(p["spec"])}</p><pre>{html.escape(tree_text(p["id"]))}</pre><p>{html.escape(p["note"])}</p></details>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>火星生产产业链森林</title><style>body{max-width:1100px;margin:40px auto;padding:0 22px;font:16px/1.6 system-ui;color:#163047;background:#f5f7f9}h1,h2{color:#243d57}details{background:white;margin:12px 0;padding:15px;border-radius:8px;border:1px solid #cfd8e3}summary{font-weight:650;cursor:pointer}pre{font:13px/1.55 ui-monospace,monospace;overflow:auto;padding:15px;background:#f3f5f7}p{color:#536779}</style><h1>火星工业—农业—能源：41棵产业链</h1><p>v0.1｜根为终端产品。每棵树物质只定义一次，共享输入用编号引用；底层为DAG。外部成套件表示尚未本地闭合，不是火星天然资源。设备质量与作物参数为设计假设。</p>'''+''.join(blocks)+'</html>'
(OUT/'产业链森林.html').write_text(page,encoding='utf-8')
print('reports generated',len(report),len(page))
