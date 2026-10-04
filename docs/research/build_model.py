from __future__ import annotations
import json, math, csv, re
from pathlib import Path
from collections import defaultdict
from functools import lru_cache
OUT=Path(__file__).resolve().parent
S={}
def src(k,title,url,note=''):
    S[k]={'id':k,'title':title,'url':url,'note':note}
src('S01','NASA Mars Fact Sheet','https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html','大气体积分数、平均摩尔质量43.49 g/mol、总质量约2.5e16 kg；非可采储量。')
src('S02','USGS SWIM probabilistic mapping (2026)','https://www.usgs.gov/publications/subsurface-water-ice-mapping-mars-a-probabilistic-approach','冰的概率分布；不是矿山储量证明。')
src('S03','NASA Utopia Planitia ice deposit','https://science.nasa.gov/resource/location-of-large-subsurface-water-ice-deposit-in-utopia-planitia-mars/','2016雷达估计约14300 km3水当量。')
src('S04','ESA suspected MFF ice','https://www.esa.int/ESA_Multimedia/Images/2024/01/Map_of_suspected_ice_at_Mars_s_equator2','2024雷达解释：22万—40万km3疑似冰，覆盖层300—600m。')
src('S05','Meslin et al. Science 2013 Table 1','https://mars.nasa.gov/files/msl/Science-2013-Meslin-.pdf','使用Portage APXS列；PDF页6，水和碳不计的归一化氧化物等效浓度。')
src('S06','Bish et al. Science 2013','https://mars.nasa.gov/files/msl/Science-2013-Bish-.pdf','Rocknest晶相相对丰度；不是整体土壤的同名百分比。')
src('S07','NASA Spirit silica-rich soil','https://science.nasa.gov/photojournal/silica-rich-soil-found-by-spirit/','局部约90%非晶二氧化硅，不是石英矿储量。')
src('S08','NASA nitrogen on Mars','https://www.nasa.gov/solar-system/nasas-curiosity-rover-finds-biologically-useful-nitrogen-on-mars/','钻孔样品硝酸盐当量最高约1100ppm。')
src('S09','NASA perchlorate overview','https://ntrs.nasa.gov/citations/20190028297','Phoenix土壤约0.5 wt%；氧氯盐鉴别有局限。')
src('S10','NASA phosphorus mobility','https://ntrs.nasa.gov/citations/20220018673','Gale局部P2O5 1.5—7.5 wt%；中值基岩0.9—1.2%。')
src('S11','NASA elemental sulfur (2024)','https://www.nasa.gov/missions/mars-science-laboratory/curiosity-rover/nasas-curiosity-rover-discovers-a-surprise-in-a-martian-rock/','确认天然单质硫；不等于工业硫矿储量。')
src('S12','NASA siderite (2025)','https://www.nasa.gov/centers-and-facilities/ames/nasas-curiosity-rover-may-have-solved-mars-missing-carbonate-mystery/','菱铁矿确认；不能直接替换石灰石矿床假设。')
src('S13','NASA Curiosity sulfate-bearing unit','https://www.nasa.gov/missions/mars-science-laboratory/curiosity-rover/nasas-curiosity-mars-rover-reaches-long-awaited-salty-region/','镁硫酸盐、钙硫酸盐和NaCl。')
src('S14','NASA boron in Catabola','https://science.nasa.gov/resource/boron-in-calcium-sulfate-vein-at-catabola-mars','2016局部B低于0.1 wt%；不是硼矿床。')
src('S15','NASA K and Th measurements','https://ntrs.nasa.gov/citations/20030066640','早期Th平均约1.1 ppm估计；不代表钍矿或可用核燃料。')
src('S16','NASA organics (2026)','https://www.nasa.gov/missions/mars-science-laboratory/curiosity-rover/nasas-curiosity-finds-organic-molecules-never-seen-before-on-mars/','痕量有机化学发现，不是可采石油。')
src('S17','ESA methane limits','https://www.esa.int/About_Us/ESAC/ExoMars_orbiter_continues_hunt_for_key_signs_of_life_on_Mars','TGO测量上限与Curiosity近地观测不一致；不得假设天然气田。')
src('S18','NASA Mars aqueous processing','https://ntrs.nasa.gov/citations/20120016264','模拟物中铁、氧化铝、氧化镁、氧化钙提取和氢还原铁；未证明火星现场规模制造。')
src('S19','DOE crystalline silicon photovoltaics','https://www.energy.gov/cmei/systems/crystalline-silicon-photovoltaics-research','石英—硅—晶锭—硅片—电池—组件；支持路线不支持本文件假设BOM。')
src('S20','DOE photovoltaic manufacturing basics','https://www.energy.gov/cmei/systems/solar-photovoltaic-manufacturing-basics','纯化、掺杂、涂层、电极、封装和电气辅件均必要。')
src('S21','NASA MOXIE completed mission','https://www.nasa.gov/solar-system/nasas-oxygen-generating-experiment-moxie-completes-mars-mission/','CO2电解火星演示；不是全部产业链已具备。')
src('S22','NASA H2 and CO material processing','https://ntrs.nasa.gov/citations/19910014303','CO2/H2生成化工产品与氧化物还原路线。')
src('S23','NASA additive construction with regolith','https://ntrs.nasa.gov/citations/20150010765','风化层模拟物烧结等建设研究；不是承压构件认证。')
src('S24','NASA Biomass Production Chamber','https://ntrs.nasa.gov/citations/20040089951','地面受控环境作物及水/碳气体流测试；不支持直接外推火星系数。')
src('S25','ESA MELiSSA compartments','https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Melissa/Closed_Loop_Compartments','农业的氧气、水、养分和废物循环。')
src('S26','ESA nitrifying compartment','https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Melissa/Compartment_III_The_nitrifying_compartment','氨氮到硝态氮；不要把所有氮肥直接视为适用水培配方。')
src('S27','NASA Mars PV design','https://ntrs.nasa.gov/citations/19910057365','约590 W/m2是大气外平均日照；地表发电还受尘埃、昼夜、姿态影响。')
src('S28','Sandia nickel-iron battery tests','https://www.sandia.gov/app/uploads/sites/163/2021/09/SAND2014-17462.pdf','NiFe路线参考；低温、低比能、水维护问题；不支持本文件假设BOM。')
src('S29','NASA calcium carbonate evidence','https://ntrs.nasa.gov/citations/20090011357','碳酸盐证据；无工业石灰石储量。')
src('S30','NASA polar water-ice estimate','https://ntrs.nasa.gov/citations/20000033862','2000年MOLA历史估计3.2—4.7百万km3；不与其他冰库直接相加。')
src('S31','NASA Odyssey instruments','https://science.nasa.gov/mission/odyssey/science-instruments/','元素分布测量与矿床储量不同。')
src('S32','NASA manganese oxides','https://www.jpl.nasa.gov/news/nasa-rover-findings-point-to-a-more-earth-like-martian-past/','局部锰氧化物证据。')
src('S34','NASA ISRU resource table','https://www.nasa.gov/wp-content/uploads/2015/03/nac_tie_december_2018_gsanders_isru.pdf','含水矿物与铁/镁/硅资源类别；不提供矿山可采储量。')
src('S33','NASA native organics (2025)','https://science.nasa.gov/missions/mars-science-laboratory/nasas-curiosity-rover-detects-largest-organic-molecules-found-on-mars/','检测/热解释放的烷烃，不等于自然纯烷烃原料库。')
src('H00','本回答设计假设','本回答设定；不是文献实测','所有设备BOM、产能名义标签、矿石品位/回收率、作物组成、良率与未量化项均需替换校准。')
resources=[]
def res(id,group,name,formula,status,abundance,inventory,use,refs,note=''):
    resources.append(dict(id=id,group=group,name=name,formula=formula,status=status,abundance=abundance,inventory=inventory,recoverable_reserve='未建立可用于本项目的已探明经济可采储量',use=use,sources=refs,note=note))
gases=[('CO₂','CO2',95.1,44.009),('N₂','N2',2.59,28.014),('Ar','Ar',1.94,39.948),('O₂','O2',.16,31.998),('CO','CO',.06,28.010),('水蒸气','H2O',.021,18.015),('Ne','Ne',.00025,20.180),('Kr','Kr',.00003,83.798),('Xe','Xe',.000008,131.293)]
for n,(name,formula,vol,mw) in enumerate(gases,1):
    mass=2.5e16*(vol/100)*mw/43.49
    res(f'G{n:02}','大气',name,formula,'观测/参考值',f'{vol:g} vol%；体积分数',f'粗略全球组分库存≈{mass:.3g} kg；按总大气质量换算，非采收承诺','气体分离；CO2为碳和氧来源；N2为氮源','S01', '不同季节/高度/纬度有变化；极低含量物质通常不作首选大宗原料。')
res('G10','大气','其他痕量与同位素气体','HDO/NO/H₂/He/O₃等','观测或物理化学存在；逐项证据不等同','不设统一稳定丰度；NASA参考表HDO约0.85ppm、NO约100ppm','未统一估计','科研/可选痕量模块','S01','未将未逐项核实的成分用作生产供给。')
res('G11','大气','甲烷','CH4','观测不一致','近地检测与轨道未检出不一致；TGO相关研究上限<0.05ppbv，常更低','无可用天然气储量','默认仅采用合成甲烷','S17')
res('W01','水与冰','两极水冰','H2O','确认','冰与尘土混合，局部品位不同','历史MOLA估计总体积约3.2—4.7×10^6 km3（2000年）','水、氢、氧、热管理','S30','历史数量级，不能与区域地下冰重复累加。')
res('W02','水与冰','中纬度浅层地下冰','H2O','多证据支持；具体区块需探测','USGS 2026模型：约45°以极方向较有利；深度与含冰量局地变化','全球可开采量未定','首选水资源候选','S02')
res('W03','水与冰','Utopia Planitia地下冰','H2O','雷达解释','覆盖层与含冰量需现场测量','2016水当量体积估计约14300 km3','区域水资源','S03')
res('W04','水与冰','Medusae Fossae疑似地下冰','H2O','有条件的雷达解释','干覆盖层约300—600m','假设富冰解释成立，约2.2—4.0×10^5 km3冰','远期情景','S04','不是已钻探确认的浅层水矿。')
res('W05','水与冰','风化层结合水/羟基','H2O/OH','确认','低中纬度水当量氢约2—10 wt%，不能全当自由水','未估算','热提水备选','S05','化学结合与自由冰开采能耗不同。')
res('W06','水与冰','二氧化碳霜/干冰','CO2','确认','季节极冠及残余极区；随季节变化','不设统一可采库存','CO2备选来源','S01')
res('W07','水与冰','深层液态水/盐水','H2O+盐','解释有争议/未钻探验证','不输入确定含量','未知','不纳入基础供水','S02','默认不可用，而非判定不存在。')
# Local oxide assay: same physical sample; must not sum with mineral table as independent stocks.
ox=[('Si','SiO2',42.88),('Fe','FeOT',19.19),('Al','Al2O3',9.43),('Mg','MgO',8.69),('Ca','CaO',7.28),('Na','Na2O',2.72),('Ti','TiO2',1.19),('P','P2O5',.94),('K','K2O',.49),('Cr','Cr2O3',.49),('Mn','MnO',.41),('S','SO3',5.45),('Cl','Cl',.69)]
for j,(el,form,val) in enumerate(ox,1):
    res(f'B{j:02}','局部整体岩土化学',el+'元素含量（氧化物等效）',form,'Portage APXS局部实测',f'{val:.2f} wt%（水/碳不计归一化）','未知；禁止由一个采样点乘全火星面积外推','材料与营养元素资源线索','S05','不是对应纯氧化物矿藏；不能视为全部可直接分离。')
minerals=[
('M01','玄武质岩石/风化层','混合硅酸盐','确认','广泛存在；无一个通用wt%','骨料、烧结、陶瓷、玄武岩棉','S05;S06'),
('M02','斜长石','(Na,Ca)(Al,Si)4O8','确认','Rocknest晶体部分40.8%','铝/硅/钙/钠候选原料','S06'),
('M03','橄榄石','(Mg,Fe)2SiO4','确认','Rocknest晶体部分22.4%','镁/铁/硅候选原料','S06'),
('M04','辉石（普通辉石/易变辉石）','复杂Mg/Fe/Ca硅酸盐','确认','Rocknest晶体部分14.6%/13.8%','材料原料','S06'),
('M05','磁铁矿','Fe3O4','确认','Rocknest晶体部分2.1%','选矿与铁源候选','S06'),
('M06','赤铁矿及其他铁氧化物','Fe2O3等','确认','局地富集；Rocknest拟合少量接近检出限','铁源候选','S06'),
('M07','二氧化硅富集物','SiO2·nH2O/非晶SiO2','确认','Spirit局部样品约90% SiO2','玻璃、硅原料候选','S07'),
('M08','石英/钛铁矿/透长石','SiO2/FeTiO3/KAlSi3O8','拟合或局部检出；部分近检测限','Rocknest晶体部分拟合1.4%/0.9%/1.3%','石英、钛、钾候选','S06'),
('M09','非晶和低结晶相','多种混合相','确认但组分不唯一','Rocknest整体约27 wt%，不确定度较大','水和多元素来源线索','S06'),
('M10','黏土/层状硅酸盐','蒙脱石等','轨道/局部观测支持','区域性；不是所有风化层都有','吸附材料、硅铝源','S06'),
('M11','石膏/半水石膏/硬石膏','CaSO4·2H2O等','确认','区域性；无全球平均矿石品位','钙硫肥、胶结材料、水','S13'),
('M12','含水硫酸镁矿物','MgSO4·nH2O','确认','区域性；水合态不同','镁硫肥、水','S13'),
('M13','黄钾铁矾/含铁硫酸盐','KFe3(SO4)2(OH)6等','已报告矿物类别','局部；不设定全球品位','硫/铁/钾候选','S34'),
('M14','氯化钠/含氯盐','NaCl等','确认/区域性','无统一工业品位','氯碱化工、盐','S13'),
('M15','高氯酸盐/氯酸盐','ClO4-/ClO3-盐','确认；物种区分有局限','Phoenix约0.5 wt%高氯酸盐','优先作为污染物；不作肥料或默认氧源','S09'),
('M16','硝酸盐','NO3-盐','热解释放气体推断支持','钻孔样品最高约1100ppm硝酸盐当量','备选氮源；首版优先大气N2','S08'),
('M17','磷酸盐/磷灰石类载磷相','Ca5(PO4)3(F,Cl,OH)等','元素与矿物学证据；矿床未定','Gale局部P2O5 1.5—7.5 wt%；基岩中值0.9—1.2%','磷肥/掺杂源候选','S10'),
('M18','碳酸盐：菱镁矿/方解石类','MgCO3/CaCO3','有证据','无统一品位；不等同大规模纯石灰石矿','钙/镁和化工候选','S29'),
('M19','菱铁矿','FeCO3','2025研究确认','局部；不外推全部硫酸盐地层','铁/碳来源候选','S12'),
('M20','天然单质硫','S','2024原位确认','局部纯硫晶体/岩石；没有总体矿石品位','硫酸/硫肥原料候选','S11'),
('M21','含硼矿脉','含B的硫酸钙矿脉','确认','2016 Catabola局部B<0.1 wt%','微量肥/硅掺杂线索','S14'),
('M22','锰氧化物','MnOx','确认','局部富集；无可采储量','合金/微量营养线索','S32'),
('M23','镍、锌、铬等微量元素载体','多种矿相','检测/陨石研究支持；矿相不全明确','不设统一可采品位','合金、电池、营养等候选','S05;S31'),
('M24','钍及其他放射性元素载体','Th/U等','Th有轨道测量；U矿床未确认','早期Th平均估计约1.1ppm；非矿石品位','远期研究，不作为首版燃料','S15'),
('M25','天然有机碳/有机分子前体','多种有机化合物','已检测；原始分子受热解解释影响','痕量；无工业级丰度','不作为石油/聚合物大宗原料','S16;S33'),
]
for id,name,form,status,abu,use,refs in minerals:
    res(id,'矿物/岩石',name,form,status,abu,'未知',use,refs,'矿物清单与整体岩土化学表描述可能为同一物质；禁止重复记账。')
for j,(name,form,use) in enumerate([
('可选钾盐矿','KCl','钾肥/KOH'),('可选铜矿','Cu矿物；矩阵CuO等效','导线/电机'),('可选镍矿','Ni矿物；矩阵NiO等效','电池/电极/催化'),('可选银矿','Ag2S等','晶硅电池电极'),('可选锡矿','SnO2','焊料'),('可选高品位铝矿','铝硅酸盐；矩阵Al2O3等效','导体/框架'),('可选硼矿/萤石矿','硼酸盐/CaF2','掺杂/化工'),('锂钴稀土及贵金属矿床','Li/Co/REE/Pt等','备选电池、磁体、催化'),('煤、石油、天然气田/天然橡胶/原生农作物','不适用','不作为天然输入')],1):
    res(f'U{j:02}','未证实经济矿藏/排除项',name,form,'未证实可用矿床；不是断言不存在','未知','未知',use,'H00','仅情景开关；默认不能自动生成可采储量。')
res('EN01','自然能量通量','太阳辐射','非物质','确认','大气外平均约590 W/m2；非地表全天均值','不适用：是通量不是库存','光伏、太阳热、农业光照','S27')
res('EN02','自然能量通量','风能/地热','非物质','存在物理机制；工程潜力地点相关','本版不设统一可用功率','不适用','候选，不纳入首版选定工艺','H00')
# Molecular weights with explicit integer stoichiometry.
A={'H':1.008,'C':12.011,'N':14.007,'O':15.999,'Si':28.085,'Fe':55.845,'Al':26.982,'S':32.06,'P':30.974,'K':39.098,'Ca':40.078,'Mg':24.305,'Cl':35.45,'Cu':63.546,'Ni':58.693,'B':10.81,'Ag':107.8682,'F':18.998,'Sn':118.710}
def mw(**atoms): return sum(A[k]*v for k,v in atoms.items())
W=mw(H=2,O=1); H2=mw(H=2); O2=mw(O=2); CO2=mw(C=1,O=2); CO=mw(C=1,O=1); NH3=mw(N=1,H=3); HNO3=mw(H=1,N=1,O=3); H2SO4=mw(H=2,S=1,O=4); H3PO4=mw(H=3,P=1,O=4)
raw=[]
def rawadd(id,name,formula,grade,recovery,status,refs): raw.append(dict(id=id,name=name,formula=formula,unit='kg有效组分当量',grade=grade,recovery=recovery,status=status,sources=refs,parameter_basis='品位与回收率为H情景值；不是资源表测定或储量'))
rawadd('R01','水冰中H₂O','H2O',.50,.90,'水冰确认；矿点未指定','S02')
rawadd('R02','大气CO₂组分','CO2',1,.90,'确认；品位1指组分而非全大气','S01')
rawadd('R03','大气N₂组分','N2',1,.80,'确认；品位1指组分而非全大气','S01')
rawadd('R04','大气Ar组分','Ar',1,.80,'确认；品位1指组分而非全大气','S01')
rawadd('R05','可用玄武质风化层','混合矿物',1,.90,'确认；需要去盐/筛选/材料鉴定','S05;S06')
rawadd('R06','富硅原料SiO₂当量','SiO2',.90,.90,'局部富集确认；光伏级纯化另需验证','S07')
rawadd('R07','铁矿Fe₂O₃当量','Fe2O3',.30,.85,'铁氧化物确认；30%为情景值','S06;S18')
rawadd('R08','碳酸钙原料CaCO₃当量','CaCO3',.10,.80,'碳酸盐证据；高品位CaCO3矿待勘探','S29')
rawadd('R09','天然硫S','S',.50,.90,'确认；规模品位未知','S11')
rawadd('R10','磷灰石Ca₅(PO₄)₃F当量','Ca5P3O12F',.02,.70,'载磷相存在；指定纯相为计算替身','S10')
rawadd('R11','可选钾盐KCl','KCl',.10,.70,'U：未确认可采钾盐矿','H00')
rawadd('R12','含水硫酸镁MgSO₄·H₂O当量','MgSO4H2O',.20,.80,'硫酸镁确认；指定水合态为计算替身','S13')
rawadd('R13','氯化钠NaCl','NaCl',.20,.80,'区域性确认','S13')
rawadd('R14','铜矿CuO当量','CuO',.01,.80,'U：不是天然CuO矿床确认','H00')
rawadd('R15','镍矿NiO当量','NiO',.01,.80,'U：不是天然NiO矿床确认','H00')
rawadd('R16','富铝矿Al₂O₃当量','Al2O3',.20,.75,'含铝矿物确认；纯化链另计','S05;S18')
rawadd('R17','可选银矿Ag₂S当量','Ag2S',.0001,.80,'U：可采矿床未确认','H00')
rawadd('R18','硼矿B₂O₃当量','B2O3',.001,.50,'B确认；矿床和纯化未知','S14')
rawadd('R19','可选萤石CaF₂','CaF2',.10,.80,'U：可采矿床未确认','H00')
rawadd('R20','可选锡矿SnO₂','SnO2',.01,.80,'U：可采矿床未确认','H00')
rawadd('R21','石膏CaSO₄·2H₂O','CaSO4H4O2',.50,.90,'矿物确认；局部品位未知','S13')
# Supplementary supplied components are explicitly outside the natural-resource boundary.
external=[
 dict(id='X01',name='电子/控制器成套件',unit='kg',note='芯片、传感器、功率器件；未展开本地晶圆厂。'),
 dict(id='X02',name='精密加工/轴承/刀具成套件',unit='kg',note='材料之外的精度、工具链外部依赖；不是原矿。'),
 dict(id='X03',name='特种膜/隔膜/催化辅材包',unit='kg',note='化学身份未冻结，不能当作本地零原料。'),
 dict(id='X04',name='光伏纯化/电池制程辅材包',unit='kg',note='反应气、蚀刻/钝化/清洁/焊接辅料占位；0.05kg/m2仅情景输入，不证明足量。'),
 dict(id='X05',name='农业微量元素/螯合配方包',unit='kg',note='B/Fe/Mn/Zn/Cu/Mo等需完整配方；不得将占位量视为可直接使用的培养配方。')]
materials={r['id']:dict(id=r['id'],name=r['name'],unit=r['unit'],kind='raw') for r in raw}
materials.update({r['id']:dict(id=r['id'],name=r['name'],unit=r['unit'],kind='external') for r in external})
recipes={}; products=[]
def recipe(id,name,inputs,outputs=None,unit='kg',kind='intermediate',basis='T',refs='H00',note=''):
    materials[id]=dict(id=id,name=name,unit=unit,kind=kind)
    recipes[id]=dict(product=id,name=name,unit=unit,inputs=inputs,coproducts=outputs or {},basis=basis,sources=refs,note=note)
def final(id,forest,name,inputs,unit='kg',outputs=None,basis='H',refs='H00',note='',spec=''):
    recipe(id,name,inputs,outputs,unit,'terminal',basis,refs,note)
    products.append(dict(id=id,forest=forest,name=name,unit=unit,basis=basis,spec=spec or '按产品名称/单位',note=note,sources=refs))
# Shared building-block routes. Inputs are gross; coproducts retained independently.
recipe('M_W','净水',{'R01':1},refs='S02',note='理想熔融净化物料值；采收、去盐与处理能耗另列。')
recipe('M_H2','氢气',{'M_W':W/H2},{'O2':O2/(2*H2)},refs='S22',note='水电解；氧气是副产品，不再次免费重复生成。')
recipe('M_O2','氧气',{'R02':2*CO2/O2},{'CO':2*CO/O2},refs='S21',note='选择CO2固体氧化物电解作为独立制氧路线。')
recipe('M_C','工艺碳',{'R02':CO2/A['C'],'M_H2':2*H2/A['C']},{'H2O':2*W/A['C']},refs='S22',note='Bosch路线理想总计量；碳的晶型/纯度和设备尚需定义。')
recipe('M_FE','还原铁',{'R07':mw(Fe=2,O=3)/(2*A['Fe']),'M_H2':3*H2/(2*A['Fe'])},{'H2O':3*W/(2*A['Fe'])},refs='S18',note='Fe2O3当量+H2；原矿矿相与还原性能不能从总FeO浓度直接推出。')
recipe('M_ST','低碳钢材料',{'M_FE':.998,'M_C':.002},basis='H/T',note='0.2%碳情景；不是合格承压/耐蚀钢标准；合金与质量控制缺口另标。')
recipe('M_CU','金属铜',{'R14':mw(Cu=1,O=1)/A['Cu'],'M_H2':H2/A['Cu']},{'H2O':W/A['Cu']},basis='T/U',note='氧化铜等效进料；真实硫化铜矿需要增加选冶路线。')
recipe('M_NI','金属镍',{'R15':mw(Ni=1,O=1)/A['Ni'],'M_H2':H2/A['Ni']},{'H2O':W/A['Ni']},basis='T/U',note='NiO当量路线；不是从任意火星岩土直接得到镍。')
recipe('M_AL','金属铝',{'R16':mw(Al=2,O=3)/(2*A['Al']),'M_C':3*A['C']/(4*A['Al'])},{'CO2':3*CO2/(4*A['Al'])},basis='T/U',note='碳阳极电解的主物料计量；电解质/槽衬/铝土分离链未量化。')
recipe('M_AG','金属银',{'R17':mw(Ag=2,S=1)/(2*A['Ag']),'M_O2':O2/(2*A['Ag'])},{'SO2':mw(S=1,O=2)/(2*A['Ag'])},basis='T/U',note='硫化银氧化总计量；矿床假设。')
recipe('M_SN','金属锡',{'R20':mw(Sn=1,O=2)/A['Sn'],'M_H2':2*H2/A['Sn']},{'H2O':2*W/A['Sn']},basis='T/U')
recipe('M_SI','工业硅',{'R06':mw(Si=1,O=2)/A['Si'],'M_C':2*A['C']/A['Si']},{'CO':2*CO/A['Si']},refs='S19',note='SiO2+2C→Si+2CO；工业硅不是太阳能级硅。')
recipe('M_SIP','太阳能级硅',{'M_SI':1/.90},basis='H',refs='S19;S20',note='90%材料收得率为假设；HCl/H2循环启动及杂质清除未由此证明。')
meoh=mw(C=1,H=4,O=1)
recipe('M_MEOH','甲醇',{'R02':CO2/meoh,'M_H2':3*H2/meoh},{'H2O':W/meoh},refs='S22')
ch2=mw(C=1,H=2)
recipe('M_PE','聚乙烯',{'M_MEOH':meoh/ch2},{'H2O':W/ch2},basis='T/H',refs='S22',note='甲醇制烯烃—聚合理想主计量；催化剂/选择性/聚合控制待校准。')
pdms=mw(Si=1,C=2,H=6,O=1)
recipe('M_PDMS','硅橡胶基体PDMS',{'M_SI':A['Si']/pdms,'M_MEOH':2*meoh/pdms},{'H2O':W/pdms},basis='T/H',note='甲基氯硅烷—水解缩聚路线的闭合氯载体理想总计量；不是工艺操作配方。')
recipe('M_GL','熔融石英玻璃',{'R06':1/.95},basis='H',refs='S07',note='95%成材率假设；光学、机械质量及纯化需验证。')
recipe('M_CER','烧结陶瓷/耐火件',{'R05':1/.90},basis='H',refs='S23',note='90%合格成材率假设；耐火等级待材料试验。')
recipe('M_FIB','玄武岩纤维/岩棉',{'R05':1/.90},basis='H',note='熔融—纤维化候选；不设万能粘结剂/工艺窗口。')
recipe('M_SEAL','填充硅橡胶',{'M_PDMS':.8,'R06':.2},basis='H',note='80/20质量配方假设；交联/添加剂、辐射及耐温资格未闭合。')
recipe('M_LUB','合成润滑基料',{'M_MEOH':meoh/ch2},{'H2O':W/ch2},basis='H/T',note='以(CH2)n近似的基料质量计量，不代表合格润滑剂或特定黏度。')
recipe('M_NH3','氨',{'R03':mw(N=2)/(2*NH3),'M_H2':3*H2/(2*NH3)},refs='S22',note='Haber-Bosch主计量；设备、纯化、催化与能量另计。')
recipe('M_HNO3','硝酸当量',{'M_NH3':NH3/HNO3,'M_O2':2*O2/HNO3},{'H2O':W/HNO3},basis='T',note='Ostwald过程总计量；催化材料在未量化项表。')
recipe('M_ACID','硫酸当量',{'R09':A['S']/H2SO4,'M_O2':1.5*O2/H2SO4,'M_W':W/H2SO4},basis='T',note='工业总计量，不是操作/安全设计。')
apat=mw(Ca=5,P=3,O=12,F=1); gypsum=mw(Ca=1,S=1,O=6,H=4)
recipe('M_PACID','磷酸当量',{'R10':apat/(3*H3PO4),'M_ACID':5*H2SO4/(3*H3PO4),'M_W':10*W/(3*H3PO4)},{'gypsum':5*gypsum/(3*H3PO4),'HF':mw(H=1,F=1)/(3*H3PO4)},basis='T',note='按氟磷灰石和湿法酸解计算；实际磷矿杂质和肥料级提纯另计。')
koh=mw(K=1,O=1,H=1); kcl=mw(K=1,Cl=1)
recipe('M_KOH','氢氧化钾',{'R11':kcl/koh,'M_W':W/koh},{'Cl2':mw(Cl=2)/(2*koh),'H2':H2/(2*koh)},basis='T/U',note='氯碱电解主计量；指定钾盐矿为假设。')
niOH=mw(Ni=1,O=2,H=2)
recipe('M_NIOH','氢氧化镍活性物质',{'R15':mw(Ni=1,O=1)/niOH,'M_W':W/niOH},basis='T/U',note='氧化镍水合总计量；电极形貌/性能不能由质量保证。')
# Industry terminals
final('I01','工业建设','烧结砖/铺面块',{'R05':1/.95},note='非承压围护；95%合格率假设',refs='S23')
final('I02','工业建设','陶瓷管/耐火件',{'M_CER':1},refs='S23')
final('I03','工业建设','岩棉/玄武岩纤维',{'M_FIB':1})
final('I04','工业建设','透明硅玻璃板',{'M_GL':11},unit='m²（厚5mm）',spec='密度2200kg/m3×0.005m×1m2=11kg；材料假设，非压力窗设计')
final('I05','工业建设','低碳钢零件',{'M_ST':1},basis='H/T',note='机加工损耗默认0；应另加良率')
final('I06','工业建设','裸铜导线',{'M_CU':1},basis='T/U',note='不包含绝缘、端接；铜矿可用性未确认')
final('I07','工业建设','PE管材/薄膜',{'M_PE':1},basis='T/H')
final('I08','工业建设','硅橡胶密封件',{'M_SEAL':1},basis='T/H')
final('I09','工业建设','润滑基料',{'M_LUB':1},basis='T/H')
final('I10','工业建设','钢制紧固件',{'M_ST':1},basis='H/T')
final('I11','工业建设','流体泵套件',{'M_ST':12,'M_CU':1.5,'M_SEAL':.2,'M_CER':1,'X01':.3,'X02':.5},unit='套（名义1kW）',spec='示例BOM，不保证扬程/流量/压力；非工程选型')
final('I12','工业建设','感应电机套件',{'M_ST':10,'M_CU':2,'M_GL':.5,'M_SEAL':.1,'X01':.5,'X02':.3},unit='套（名义1kW）',spec='避免稀土永磁体；绕组绝缘与叠片等级未冻结')
final('I13','工业建设','储液/储气容器套件',{'M_ST':60,'M_SEAL':.2,'M_CU':.5,'X01':.2,'X02':.3},unit='套（容积1m³）',spec='容积标签，不提供压力等级；壁厚与疲劳需独立设计')
final('I14','工业建设','电热炉套件',{'M_ST':5,'M_CER':10,'M_CU':.5,'M_C':.5,'X01':.2,'X03':.1},unit='套（名义1kW输入）',spec='加热元件、炉温与产能需独立设计')
final('I15','工业建设','机加工设备套件',{'M_ST':100,'M_CU':3,'M_CER':2,'M_LUB':1,'X01':2,'X02':1},unit='套（名义1kW主驱动）',spec='概念质量清单，不能由质量保证机床精度')
final('I16','工业建设','净水设备套件',{'M_ST':20,'M_PE':5,'M_GL':1,'M_CU':1,'M_SEAL':.5,'X03':.2,'X01':.5},unit='套（名义1m³/日）',spec='膜/过滤/传感外购；不同污染物需不同工艺')
final('I17','工业建设','气体处理设备套件',{'M_ST':20,'M_CU':2,'M_GL':2,'R06':2,'M_SEAL':.5,'X03':1,'X01':.5},unit='套（名义1kg CO₂/小时）',spec='分离组件性能另测；气体产品回收率不是由BOM确定')
final('I18','工业建设','居住/厂房围护构件套件',{'M_ST':20,'M_GL':11,'M_FIB':5,'M_PE':1,'M_SEAL':.2,'X02':.1},unit='m²围护面',spec='围护面而非建筑面积；不包含全部屏蔽层、气密和结构认证')
final('I19','工业建设','机械阀门套件',{'M_ST':.9,'M_SEAL':.03,'X02':.02},unit='件（示例小型阀）')
final('I20','工业建设','绝缘电缆',{'M_CU':.8,'M_PE':.2},unit='kg',spec='80%铜/20%PE质量假设；电压、截面和耐温另定')
# Agriculture fertilizers
can=mw(Ca=1,N=2,O=6)
final('A01','农业','净水',{'M_W':1},basis='T',refs='S02')
final('A02','农业','无水硝酸钙肥料当量',{'R08':mw(Ca=1,C=1,O=3)/can,'M_HNO3':2*HNO3/can},{ } if False else 'kg',outputs={'CO2':CO2/can,'H2O':W/can},basis='T',note='按纯盐主计量；不是可直接投放的完整水培配方')
mapw=mw(N=1,H=6,P=1,O=4)
final('A03','农业','磷酸一铵肥料当量',{'M_NH3':NH3/mapw,'M_PACID':H3PO4/mapw},basis='T',note='需与硝态氮及其他盐配平；非万能肥')
kso=mw(K=2,S=1,O=4)
final('A04','农业','硫酸钾肥料',{'R11':2*kcl/kso,'M_ACID':H2SO4/kso},outputs={'HCl':2*mw(H=1,Cl=1)/kso},basis='T/U',note='以假设钾盐矿为条件；未证实则不能开工')
mgmono=mw(Mg=1,S=1,O=5,H=2); mghepta=mw(Mg=1,S=1,O=11,H=14)
final('A05','农业','七水硫酸镁肥料',{'R12':mgmono/mghepta,'M_W':6*W/mghepta},basis='T',note='假定原料为一水盐当量，非所有天然镁盐的通用换算')
final('A06','农业','石膏钙硫肥',{'R21':1},basis='T',note='纯化检验另计；A03酸解副产石膏可替代部分需求但不能双算')
# Crops: explicit H mass-balance surrogate, not agronomic operating recipe.
# Whole plant nutrient elemental targets per kg dry biomass, not edible nutritional composition.
crop_params=[('A07','小麦可食干物质',.45,.45,.065,.024,.004,.025,.007,.003,80),('A08','大豆可食干物质',.40,.48,.067,.055,.006,.028,.012,.004,95),('A09','马铃薯可食干物质',.75,.44,.065,.020,.004,.030,.008,.003,100),('A10','叶菜可食干物质',.85,.40,.060,.035,.005,.050,.020,.005,30)]
# Need named salts already defined; all supplemental trace package mass is a design assumption.
for pid,name,hi,fc,fh,fn,fp,fk,fca,fmg,days in crop_params:
    bm=1/hi
    pmap=fp/(A['P']/mapw)
    n_from_map=pmap*(A['N']/mapw)
    nca=max(0,fn-n_from_map)/(2*A['N']/can)
    # Nitrate route may oversupply Ca; do not silently treat as precision formulation.
    kfert=fk/(2*A['K']/kso)
    mgfert=fmg/(A['Mg']/mghepta)
    ca_from_nitrate=nca*A['Ca']/can
    gyp=max(0,fca-ca_from_nitrate)/(A['Ca']/gypsum)
    gross_transp=200.0*bm
    # Hydrogen fixation proxy, plus 2% uncollected transpired water, includes mineral-hydration effects as approximation.
    directwater=(fh*W/(2*A['H'])+4.0)*bm
    inp={'R02':fc*CO2/A['C']*bm,'M_W':directwater,'A02':nca*bm,'A03':pmap*bm,'A04':kfert*bm,'A05':mgfert*bm,'X05':.001*bm}
    if gyp>0: inp['A06']=gyp*bm
    final(pid,'农业',name,inp,unit='kg可食干物质',basis='H',refs='S24;S25',spec=f'假设收获指数{hi:g}；周期{days}日；同类不代表统一品种/栽培参数',note='作物列仅预核算占位：净固定碳代理+养分元素目标+98%蒸腾冷凝回收；盐氮/钙可能过供，必须经营养配方优化替换。种源为初始生物资本，不是火星天然原料。')
    products[-1]['crop']={'harvest_index':hi,'carbon_fraction':fc,'hydrogen_fraction':fh,'N':fn,'P':fp,'K':fk,'Ca':fca,'Mg':fmg,'duration_days':days,'transpiration_kg':gross_transp,'condensate_recovery':.98,'inedible_dry_kg':bm-1}
final('A11','农业','循环水培栽培模块',{'M_ST':5,'M_PE':3,'M_FIB':1,'I11':.05,'X01':.1},unit='m²栽培面积',refs='S25',spec='不含围护壳、灯具与初始营养液；它们通过资本/服务清单另设',note='种子、苗木、微生物由地球引入或本地繁育；不可从矿物直接生成。')
# Energy terminals
# Chosen PV scenario: glass-glass, local frame, conventional Si/Ag cell; not a validated Mars design.
si_mass=2330*.00018*.90
recipe('M_CELL','晶硅电池片组',{'M_SIP':si_mass/.65,'M_AG':.008,'M_AL':.02,'R18':.00001,'R10':.00002,'M_CU':.02,'X04':.05},unit='组/m²组件',basis='H',refs='S19;S20',note='硅片180µm、有效覆盖率90%、切片收得率65%；掺杂/金属/辅料均情景值；不得视为可生产电池配方。')
final('E01','能源','晶硅太阳能板',{'M_CELL':1,'M_GL':8.8,'M_AL':1,'M_CU':.12,'M_SN':.01,'M_PDMS':.6,'X01':.05},unit='m²组件',refs='S19;S20',spec='双玻总厚4mm；硅180µm覆盖90%；组件效率假设18%；不含支架/逆变系统',note='高级/条件性本地制造；真实电池制程辅料与合格率尚未闭合。启动阶段可进口电池片而本地封装，但该替代路线未混入本矩阵。')
final('E02','能源','太阳热集热板',{'M_GL':5.5,'M_ST':6,'M_CU':.5,'M_FIB':2,'M_SEAL':.1,'X03':.02},unit='m²集热面积',spec='2.5mm透明板；选择性涂层占位；集热效率另定')
cp=.84; dt=300; util=.85
final('E03','能源','岩石显热储热模块',{'R05':3600/(cp*dt*util),'M_ST':2,'M_FIB':2},unit='kWhₜₕ名义容量',spec='cp=0.84kJ/(kgK)、ΔT=300K、可用率85%；均为设计假设',note='制造该容量不是已经存有热能；充热另需能量。')
final('E04','能源','碱性水电解设备',{'M_ST':15,'M_NI':1,'M_CU':1,'M_PE':1,'M_SEAL':.2,'M_KOH':.5,'X01':.5,'X03':.2},unit='套（1kW额定输入）',spec='Ni/KOH为条件原料；电耗另设，不由质量清单推出产氢量')
final('E05','能源','甲烷合成设备',{'M_ST':30,'M_NI':.5,'M_CU':2,'M_CER':5,'M_SEAL':.3,'X01':1,'X03':.1},unit='套（名义1kg CH₄/日）',spec='Sabatier设备概念BOM；压缩/热交换/净化需匹配')
ch4=mw(C=1,H=4)
final('E06','能源','合成甲烷',{'R02':CO2/ch4,'M_H2':4*H2/ch4},outputs={'H2O':2*W/ch4},basis='T',refs='S22',note='毛水量含上游电解；工艺回水单独列出。')
final('E07','能源','氢气',{'M_H2':1},basis='T',refs='S22')
final('E08','能源','氧气',{'M_O2':1},basis='T',refs='S21',note='独立CO2电解列；已有副产氧时不应机械叠加本列。')
final('E09','能源','镍铁蓄电池模块',{'M_NIOH':6,'M_FE':3,'M_ST':10,'M_KOH':2,'M_W':8,'M_PE':2,'M_CU':.5,'X03':.5},unit='kWhₑ名义容量',refs='S28',spec='示例质量配方，不保证1kWh性能；需保温、水维护，镍矿为未证实门槛',note='电池是储能不是一次能源；初次充电和充放效率另计。')
final('E10','能源','甲烷—氧气发电机套件',{'M_ST':60,'M_CU':4,'M_CER':1,'M_SEAL':.3,'X01':1,'X02':2},unit='套（1kWₑ名义输出）',spec='封闭/稀释工质与散热系统需设计；不能套用地球吸气式发动机',note='消耗甲烷与氧；不产生净能源。')
# Recursively aggregate gross raw requirements and separately propagated coproducts.
@lru_cache(None)
def expand(pid):
    if pid in {x['id'] for x in raw+external}: return ({pid:1.0},{})
    rec=recipes[pid]; rr=defaultdict(float); cc=defaultdict(float)
    for child,amount in rec['inputs'].items():
        a,b=expand(child)
        for k,v in a.items(): rr[k]+=amount*v
        for k,v in b.items(): cc[k]+=amount*v
    for k,v in rec['coproducts'].items(): cc[k]+=v
    return dict(rr),dict(cc)
for p in products:
    a,b=expand(p['id']);p['gross_raw']=a;p['coproducts']=b
    p['fresh_water_ideal']=max(0,a.get('R01',0)-b.get('H2O',0))
    p['external_dependency']=any(k.startswith('X') and v>0 for k,v in a.items())
    p['speculative_ore_dependency']=any(k in {'R11','R14','R15','R17','R19','R20'} and v>0 for k,v in a.items())
# Forest projection: collapse unit-transfer terminal aliases; each material is defined once.
material_aliases={}
for p in products:
    r=recipes[p['id']]
    if len(r['inputs'])==1 and not r['coproducts']:
        child,amount=next(iter(r['inputs'].items()))
        if amount==1 and child in recipes and materials[child]['unit']==p['unit']:
            material_aliases[p['id']]=child

def canonical_material(id):
    while id in material_aliases:
        id=material_aliases[id]
    return id

forests={}
for p in products:
    visited={};nodes=[];tree_edges=[];shared_edges=[]
    def walk(id,parent=None,depth=0):
        canonical=canonical_material(id)
        if canonical in visited:
            shared_edges.append({'parent':parent,'target':visited[canonical]});return
        display_id=p['id'] if parent is None else canonical
        visited[canonical]=display_id
        nodes.append({'id':display_id,'parent':parent,'depth':depth,
                      **materials[display_id],'canonical_material_id':canonical})
        if parent:tree_edges.append({'parent':parent,'child':display_id})
        for ch in recipes.get(canonical,{}).get('inputs',{}):walk(ch,display_id,depth+1)
    walk(p['id'])
    forests[p['id']]={'nodes':nodes,'tree_edges':tree_edges,'shared_edges':shared_edges,
                     'root_material_alias':material_aliases.get(p['id'])}
# Explicit unresolved issues; these cannot silently turn into zero or claims of whole-supply-chain closure.
gaps=[
('所有矿物列','矿山勘探与真实品位','没有确定坐标、矿体体积、矿相和回收试验；R矩阵为有效组分当量而非实际开挖量。'),
('所有工艺','能耗/热管理/功率/时间','物料矩阵不包含全流程kWh、温度等级、设备寿命及工时；需要另建过程约束。'),
('I05/I10/承压构件','钢种及质量资格','0.2%C假设不是压力容器钢/耐蚀钢；焊接、疲劳、无损检测和防腐未闭合。'),
('I06/I12/E01/E09','铜镍银锡矿','元素可能存在不等于已知可采矿床；无矿则必须关停或显式进口。'),
('I07/I08/I09','聚合物/密封/润滑完整配方','催化剂、分子量、交联剂、添加剂和性能尚未量化；主原料数值不是可执行配方。'),
('E01/M_CELL','完整光伏工艺清单','半导体级纯化、掺杂活化、表面钝化、刻蚀、气体/液体循环及报废损耗待工程设计。X04只是占位。'),
('M_AL','铝电解辅助链','氟盐电解质/电极/槽衬等未量化；R19在主矩阵为0不代表铝链不需要含氟辅材。'),
('A07—A10','作物营养与呼吸模型','H系数是预核算占位，盐配方可能过供Ca/S/N；光合/呼吸及O2副产不可用此矩阵精确推导。'),
('A07—A11','种源与生态资本','种子、种苗、菌种需初始引入并繁育；不得设为火星天然矿物原料。'),
('A07—A11','农业设施与服务','温室、照明、消毒、CO2回收、温控和土地/周期容量未摊入每kg食品；不是无需这些投入。'),
('E09','电池性能','示例BOM不保证额定容量/循环寿命/低温性能；需替换实测电极和整机资料。'),
('E10','甲烷氧气发电','不能直接在纯氧中运行普通空气内燃机；工质稀释、材料温度和冷却必须独立设计。'),
('全部矩阵','副产品与循环','单产品毛投入可用于独立任务核算；多产品联产必须使用过程投入/产出，避免水/氧/石膏/氢重复计数。'),
('U矿藏','存在性门控','未知储量=null且默认未解锁；不得填0或无限，也不得自动加入库存。')]
operations=[
 dict(id='OP01',name='光伏发电',output='1kWh电',input='入射到板面的光能=3.6/η_PV MJ；η假设0.18→20MJ',capital='E01面积和电气配套',note='590W/m2为大气外参考；用当地逐时板面辐照度积分。硬件矩阵太阳光用量为0并不表示发电不用太阳。'),
 dict(id='OP02',name='太阳集热',output='1kWh热',input='板面光能=3.6/η_th MJ；η假设0.5→7.2MJ',capital='E02面积',note='热的温度等级必须匹配需求。'),
 dict(id='OP03',name='储热放热',output='1kWh可用热',input='充热≥1/η_roundtrip kWh',capital='E03容量',note='制造容量与运行充热分开；储热不是能源来源。'),
 dict(id='OP04',name='电池放电',output='1kWh电',input='充电≥1/η_roundtrip kWh',capital='E09容量',note='效率、SOC、功率、保温与维护水单列。'),
 dict(id='OP05',name='甲烷氧气发电',output='1kWh电',input='甲烷=3.6/(LHV_CH4·η_gen)kg；氧气=4×甲烷（简化整数化学式）',capital='E10功率及散热',note='LHV与效率输入另定；可回收CO2/H2O，不给出免费能量。'),
 dict(id='OP06',name='水电解',output='1kg H2 +7.9360kg O2',input='8.9360kg水+正电能',capital='E04',note='精确值以摩尔质量参数计算；电耗不能从质量矩阵推断。'),
 dict(id='OP07',name='农业生长',output='1kg可食干物质',input='A07—A10资源+光照+热管理+种植面积×生长时长',capital='A11+围护+灯具/太阳导光',note='同化CO2不同于从外界新增开采CO2；循环CO2库存另建。')]
# consistency checks
assert len(products)==41
for p in products:
    assert all(v>=-1e-10 and math.isfinite(v) for v in p['gross_raw'].values())
    ids=[x['id'] for x in forests[p['id']]['nodes']]
    assert len(ids)==len(set(ids))
# chemical mass checks for selected core reactions using atomic mass conservation
checks=[]
def chk(name,lhs,rhs):
    err=lhs-rhs; checks.append(dict(check=name,left_kg_per_mol=lhs/1000,right_kg_per_mol=rhs/1000,abs_error=abs(err),passed=abs(err)<1e-8));assert abs(err)<1e-8
chk('水电解',2*W,2*H2+O2)
chk('Sabatier',CO2+4*H2,ch4+2*W)
chk('铁氧化物氢还原',mw(Fe=2,O=3)+3*H2,2*A['Fe']+3*W)
chk('硅碳热还原',mw(Si=1,O=2)+2*A['C'],A['Si']+2*CO)
chk('磷灰石湿法',apat+5*H2SO4+10*W,3*H3PO4+5*gypsum+mw(H=1,F=1))
chk('CO2电解',2*CO2,2*CO+O2)
model=dict(version='0.1',date='2026-10-03',boundary='概念生产仿真：21类有效原料当量，41类终端产品；非完整可执行工程BOM。',sources=S,resources=resources,raw_materials=raw,external_inputs=external,materials=materials,recipes=recipes,products=products,forests=forests,material_aliases=material_aliases,gaps=gaps,operations=operations,checks=checks,atomic_masses=A)
(OUT/'mars_model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
# CSV matrix with terminal products across columns
for mode in ['gross','fresh_water_ideal','mine_scenario']:
    with (OUT/f'matrix_{mode}.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['原料ID','原料','原料单位']+[f"{p['id']} {p['name']} / {p['unit']}" for p in products])
        for r in raw:
            vals=[]
            for p in products:
                v=p['gross_raw'].get(r['id'],0)
                if mode=='fresh_water_ideal' and r['id']=='R01':v=p['fresh_water_ideal']
                if mode=='mine_scenario':v=v/r['grade']/r['recovery']
                vals.append(v)
            w.writerow([r['id'],r['name'],r['unit'] if mode!='mine_scenario' else 'kg情景进料']+vals)
with (OUT/'matrix_external.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['输入ID','输入','单位']+[p['id'] for p in products])
    for r in external:w.writerow([r['id'],r['name'],r['unit']]+[p['gross_raw'].get(r['id'],0) for p in products])
with (OUT/'resource_catalogue.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(resources[0]));w.writeheader();w.writerows(resources)
with (OUT/'product_catalogue.csv').open('w',encoding='utf-8-sig',newline='') as f:
    keys=['id','forest','name','unit','basis','spec','note','external_dependency','speculative_ore_dependency','sources'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(products)
print(json.dumps({'resources':len(resources),'raw':len(raw),'products':len(products),'recipes':len(recipes),'checks':len(checks),'nonzero_matrix_entries':sum(sum(v>0 for k,v in p['gross_raw'].items() if k.startswith('R')) for p in products)},ensure_ascii=False))
