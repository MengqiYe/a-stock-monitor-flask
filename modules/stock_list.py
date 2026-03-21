# 上证50、中证500成分股、指数、港股列表
# 数据来源：上海证券交易所、中证指数公司

# ==================== 指数数据 ====================

# 主要指数
MAIN_INDICES = [
    {'code': '000001', 'name': '上证指数', 'market': 'sh', 'description': '上海证券交易所综合股价指数'},
    {'code': '399001', 'name': '深证成指', 'market': 'sz', 'description': '深圳证券交易所成份股价指数'},
    {'code': '399006', 'name': '创业板指', 'market': 'sz', 'description': '创业板综合指数'},
    {'code': '000016', 'name': '上证50', 'market': 'sh', 'description': '上证50指数成分股'},
    {'code': '000300', 'name': '沪深300', 'market': 'sh', 'description': '沪深300指数成分股'},
    {'code': '000905', 'name': '中证500', 'market': 'sh', 'description': '中证500指数成分股'},
    {'code': '000852', 'name': '中证1000', 'market': 'sh', 'description': '中证1000指数成分股'},
    {'code': '399005', 'name': '中小板指', 'market': 'sz', 'description': '中小板综合指数'},
    {'code': '399102', 'name': '创业板综', 'market': 'sz', 'description': '创业板综合指数'},
]

# 指数成分股映射（指数代码 -> 成分股代码列表）
INDEX_COMPONENTS = {
    '000016': 'sz50',      # 上证50 -> SZ50_STOCKS
    '000300': 'hs300',     # 沪深300 -> 上证50 + 中证500部分
    '000905': 'zz500',     # 中证500 -> ZZ500_STOCKS
    '000852': 'zz1000',    # 中证1000 -> 小盘股
}

# ==================== 上证50成分股（50只）====================
SZ50_STOCKS = [
    {'code': '600000', 'name': '浦发银行'}, {'code': '600036', 'name': '招商银行'},
    {'code': '600519', 'name': '贵州茅台'}, {'code': '600887', 'name': '伊利股份'},
    {'code': '600900', 'name': '长江电力'}, {'code': '601318', 'name': '中国平安'},
    {'code': '601398', 'name': '工商银行'}, {'code': '601857', 'name': '中国石油'},
    {'code': '601988', 'name': '中国银行'}, {'code': '601288', 'name': '农业银行'},
    {'code': '600030', 'name': '中信证券'}, {'code': '601166', 'name': '兴业银行'},
    {'code': '600276', 'name': '恒瑞医药'}, {'code': '600585', 'name': '海螺水泥'},
    {'code': '600690', 'name': '海尔智家'}, {'code': '600809', 'name': '山西汾酒'},
    {'code': '601888', 'name': '中国中免'}, {'code': '600309', 'name': '万华化学'},
    {'code': '600406', 'name': '国电南瑞'}, {'code': '600031', 'name': '三一重工'},
    {'code': '601818', 'name': '光大银行'}, {'code': '600016', 'name': '民生银行'},
    {'code': '601658', 'name': '邮储银行'}, {'code': '600009', 'name': '上海机场'},
    {'code': '600048', 'name': '保利发展'}, {'code': '600028', 'name': '中国石化'},
    {'code': '601939', 'name': '建设银行'}, {'code': '601728', 'name': '中国电信'},
    {'code': '601328', 'name': '交通银行'}, {'code': '600837', 'name': '海通证券'},
    {'code': '600346', 'name': '恒力石化'}, {'code': '601668', 'name': '中国建筑'},
    {'code': '600176', 'name': '中国巨石'}, {'code': '600352', 'name': '浙江龙盛'},
    {'code': '601688', 'name': '华泰证券'}, {'code': '600111', 'name': '北方稀土'},
    {'code': '601138', 'name': '工业富联'}, {'code': '600019', 'name': '宝钢股份'},
    {'code': '601919', 'name': '中远海控'}, {'code': '601816', 'name': '京沪高铁'},
    {'code': '600703', 'name': '三安光电'}, {'code': '600893', 'name': '航发动力'},
    {'code': '600588', 'name': '用友网络'}, {'code': '601998', 'name': '中信银行'},
    {'code': '601877', 'name': '正泰电器'}, {'code': '601012', 'name': '隆基绿能'},
    {'code': '600489', 'name': '中金黄金'}, {'code': '600660', 'name': '福耀玻璃'},
]

# ==================== 中证500成分股（精选200只代表性股票）====================
ZZ500_STOCKS = [
    # 深市主板 000xxx
    {'code': '000001', 'name': '平安银行'}, {'code': '000002', 'name': '万科A'},
    {'code': '000063', 'name': '中兴通讯'}, {'code': '000069', 'name': '华侨城A'},
    {'code': '000100', 'name': 'TCL科技'}, {'code': '000157', 'name': '中联重科'},
    {'code': '000333', 'name': '美的集团'}, {'code': '000338', 'name': '潍柴动力'},
    {'code': '000425', 'name': '徐工机械'}, {'code': '000568', 'name': '泸州老窖'},
    {'code': '000625', 'name': '长安汽车'}, {'code': '000651', 'name': '格力电器'},
    {'code': '000661', 'name': '长春高新'}, {'code': '000708', 'name': '中信特钢'},
    {'code': '000725', 'name': '京东方A'}, {'code': '000768', 'name': '中航西飞'},
    {'code': '000776', 'name': '广发证券'}, {'code': '000783', 'name': '长江证券'},
    {'code': '000858', 'name': '五粮液'}, {'code': '000876', 'name': '新希望'},
    {'code': '000895', 'name': '双汇发展'}, {'code': '000938', 'name': '紫光股份'},
    {'code': '000963', 'name': '华东医药'}, {'code': '000977', 'name': '浪潮信息'},
    {'code': '001979', 'name': '招商蛇口'},
    # 中小板 002xxx
    {'code': '002001', 'name': '新和成'}, {'code': '002007', 'name': '华兰生物'},
    {'code': '002008', 'name': '大族激光'}, {'code': '002027', 'name': '分众传媒'},
    {'code': '002049', 'name': '紫光国微'}, {'code': '002050', 'name': '三花智控'},
    {'code': '002129', 'name': 'TCL中环'}, {'code': '002142', 'name': '宁波银行'},
    {'code': '002230', 'name': '科大讯飞'}, {'code': '002236', 'name': '大华股份'},
    {'code': '002241', 'name': '歌尔股份'}, {'code': '002271', 'name': '东方雨虹'},
    {'code': '002304', 'name': '洋河股份'}, {'code': '002311', 'name': '海大集团'},
    {'code': '002352', 'name': '顺丰控股'}, {'code': '002410', 'name': '广联达'},
    {'code': '002415', 'name': '海康威视'}, {'code': '002460', 'name': '赣锋锂业'},
    {'code': '002466', 'name': '天齐锂业'}, {'code': '002475', 'name': '立讯精密'},
    {'code': '002493', 'name': '荣盛石化'}, {'code': '002594', 'name': '比亚迪'},
    {'code': '002601', 'name': '龙佰集团'}, {'code': '002648', 'name': '卫星化学'},
    {'code': '002432', 'name': '九安医疗'}, {'code': '002714', 'name': '牧原股份'},
    {'code': '002821', 'name': '凯莱英'}, {'code': '002841', 'name': '视源股份'},
    {'code': '002938', 'name': '鹏鼎控股'},
    # 创业板 300xxx
    {'code': '300003', 'name': '乐普医疗'}, {'code': '300014', 'name': '亿纬锂能'},
    {'code': '300015', 'name': '爱尔眼科'}, {'code': '300033', 'name': '同花顺'},
    {'code': '300037', 'name': '新宙邦'}, {'code': '300059', 'name': '东方财富'},
    {'code': '300070', 'name': '碧水源'}, {'code': '300122', 'name': '智飞生物'},
    {'code': '300124', 'name': '汇川技术'}, {'code': '300142', 'name': '沃森生物'},
    {'code': '300144', 'name': '宋城演艺'}, {'code': '300274', 'name': '阳光电源'},
    {'code': '300308', 'name': '中际旭创'}, {'code': '300347', 'name': '泰格医药'},
    {'code': '300408', 'name': '三环集团'}, {'code': '300413', 'name': '芒果超媒'},
    {'code': '300433', 'name': '蓝思科技'}, {'code': '300450', 'name': '先导智能'},
    {'code': '300454', 'name': '深信服'}, {'code': '300496', 'name': '中科创达'},
    {'code': '300498', 'name': '温氏股份'}, {'code': '300529', 'name': '健帆生物'},
    {'code': '300661', 'name': '圣邦股份'}, {'code': '300750', 'name': '宁德时代'},
    {'code': '300760', 'name': '迈瑞医疗'}, {'code': '300782', 'name': '卓胜微'},
    {'code': '300896', 'name': '爱美客'},
    # 沪市主板 600xxx
    {'code': '600006', 'name': '东风汽车'}, {'code': '600008', 'name': '首创环保'},
    {'code': '600010', 'name': '包钢股份'}, {'code': '600011', 'name': '华能国际'},
    {'code': '600015', 'name': '华夏银行'}, {'code': '600017', 'name': '日照港'},
    {'code': '600018', 'name': '上港集团'}, {'code': '600021', 'name': '上海电力'},
    {'code': '600022', 'name': '山东钢铁'}, {'code': '600023', 'name': '浙能电力'},
    {'code': '600025', 'name': '华能水电'}, {'code': '600026', 'name': '中远海能'},
    {'code': '600027', 'name': '华电国际'}, {'code': '600029', 'name': '南方航空'},
    {'code': '600050', 'name': '中国联通'}, {'code': '600104', 'name': '上汽集团'},
    {'code': '600109', 'name': '国金证券'}, {'code': '600115', 'name': '中国东航'},
    {'code': '600132', 'name': '重庆啤酒'}, {'code': '600150', 'name': '中国船舶'},
    {'code': '600153', 'name': '建发股份'}, {'code': '600160', 'name': '巨化股份'},
    {'code': '600170', 'name': '上海建工'}, {'code': '600177', 'name': '雅戈尔'},
    {'code': '600183', 'name': '生益科技'}, {'code': '600188', 'name': '兖州煤业'},
    {'code': '600196', 'name': '复星医药'}, {'code': '600219', 'name': '南山铝业'},
    {'code': '600256', 'name': '广汇能源'}, {'code': '600298', 'name': '安琪酵母'},
    {'code': '600332', 'name': '白云山'}, {'code': '600348', 'name': '华阳股份'},
    {'code': '600362', 'name': '江西铜业'}, {'code': '600377', 'name': '宁沪高速'},
    {'code': '600383', 'name': '金地集团'}, {'code': '600398', 'name': '海澜之家'},
    {'code': '600436', 'name': '片仔癀'}, {'code': '600438', 'name': '通威股份'},
    {'code': '600460', 'name': '士兰微'}, {'code': '600482', 'name': '中国动力'},
    {'code': '600487', 'name': '亨通光电'}, {'code': '600498', 'name': '烽火通信'},
    {'code': '600507', 'name': '方大特钢'}, {'code': '600522', 'name': '中天科技'},
    {'code': '600536', 'name': '中国软件'}, {'code': '600547', 'name': '山东黄金'},
    {'code': '600549', 'name': '厦门钨业'}, {'code': '600570', 'name': '恒生电子'},
    {'code': '600580', 'name': '卧龙电驱'}, {'code': '600582', 'name': '天地科技'},
    {'code': '600584', 'name': '长电科技'}, {'code': '600587', 'name': '新华医疗'},
    {'code': '600598', 'name': '北大荒'},
    # 沪市主板 601xxx
    {'code': '601006', 'name': '大秦铁路'}, {'code': '601009', 'name': '南京银行'},
    {'code': '601012', 'name': '隆基绿能'}, {'code': '601018', 'name': '宁波港'},
    {'code': '601021', 'name': '春秋航空'}, {'code': '601066', 'name': '中信建投'},
    {'code': '601088', 'name': '中国神华'}, {'code': '601100', 'name': '恒立液压'},
    {'code': '601111', 'name': '中国国航'}, {'code': '601117', 'name': '中国化学'},
    {'code': '601155', 'name': '新城控股'}, {'code': '601168', 'name': '西部矿业'},
    {'code': '601169', 'name': '北京银行'}, {'code': '601186', 'name': '中国铁建'},
    {'code': '601211', 'name': '国泰君安'}, {'code': '601225', 'name': '陕西煤业'},
    {'code': '601229', 'name': '上海银行'}, {'code': '601233', 'name': '桐昆股份'},
    {'code': '601238', 'name': '广汽集团'}, {'code': '601298', 'name': '青岛港'},
    {'code': '601319', 'name': '中国人保'}, {'code': '601336', 'name': '新华保险'},
    {'code': '601390', 'name': '中国中铁'}, {'code': '601600', 'name': '中国铝业'},
    {'code': '601601', 'name': '中国太保'}, {'code': '601607', 'name': '上海医药'},
    {'code': '601611', 'name': '中国核建'}, {'code': '601615', 'name': '明阳智能'},
    {'code': '601618', 'name': '中国中冶'}, {'code': '601628', 'name': '中国人寿'},
    {'code': '601633', 'name': '长城汽车'}, {'code': '601666', 'name': '平煤股份'},
    {'code': '601669', 'name': '中国电建'}, {'code': '601689', 'name': '拓普集团'},
    {'code': '601699', 'name': '潞安环能'}, {'code': '601717', 'name': '郑煤机'},
    {'code': '601727', 'name': '上海电气'}, {'code': '601766', 'name': '中国中车'},
    {'code': '601788', 'name': '光大证券'}, {'code': '601799', 'name': '星宇股份'},
    {'code': '601800', 'name': '中国交建'}, {'code': '601808', 'name': '中海油服'},
    {'code': '601838', 'name': '成都银行'}, {'code': '601868', 'name': '中国能建'},
    {'code': '601872', 'name': '招商轮船'}, {'code': '601878', 'name': '浙商证券'},
    {'code': '601898', 'name': '中煤能源'}, {'code': '601899', 'name': '紫金矿业'},
    {'code': '601901', 'name': '方正证券'}, {'code': '601916', 'name': '浙商银行'},
    {'code': '601933', 'name': '永辉超市'}, {'code': '601985', 'name': '中国核电'},
    {'code': '601989', 'name': '中国重工'}, {'code': '601991', 'name': '大唐发电'},
    {'code': '601992', 'name': '金隅集团'}, {'code': '601995', 'name': '中金公司'},
    # 沪市主板 603xxx
    {'code': '603005', 'name': '晶方科技'}, {'code': '603019', 'name': '中科曙光'},
    {'code': '603026', 'name': '石大胜华'}, {'code': '603027', 'name': '千禾味业'},
    {'code': '603077', 'name': '和邦生物'}, {'code': '603160', 'name': '汇顶科技'},
    {'code': '603195', 'name': '公牛集团'}, {'code': '603198', 'name': '迎驾贡酒'},
    {'code': '603236', 'name': '移远通信'}, {'code': '603259', 'name': '药明康德'},
    {'code': '603260', 'name': '合盛硅业'}, {'code': '603288', 'name': '海天味业'},
    {'code': '603290', 'name': '斯达半导'}, {'code': '603355', 'name': '莱克电气'},
    {'code': '603369', 'name': '今世缘'}, {'code': '603444', 'name': '吉比特'},
    {'code': '603456', 'name': '九洲药业'}, {'code': '603482', 'name': '锦浪科技'},
    {'code': '603486', 'name': '科沃斯'}, {'code': '603502', 'name': '华友钴业'},
    {'code': '603515', 'name': '欧派家居'}, {'code': '603517', 'name': '绝味食品'},
    {'code': '603556', 'name': '海兴电力'}, {'code': '603562', 'name': '明泰铝业'},
    {'code': '603577', 'name': '汇川技术'}, {'code': '603583', 'name': '口子窖'},
    {'code': '603588', 'name': '高能环境'}, {'code': '603593', 'name': '圣农发展'},
    {'code': '603596', 'name': '伯特利'}, {'code': '603605', 'name': '珀莱雅'},
    {'code': '603606', 'name': '东方电缆'}, {'code': '603612', 'name': '索通发展'},
    {'code': '603613', 'name': '国联股份'}, {'code': '603638', 'name': '艾迪精密'},
    {'code': '603650', 'name': '彤程新材'}, {'code': '603659', 'name': '璞泰来'},
    {'code': '603666', 'name': '信捷电气'}, {'code': '603688', 'name': '石英股份'},
    {'code': '603707', 'name': '健盛集团'}, {'code': '603708', 'name': '家家悦'},
    {'code': '603712', 'name': '七一二'}, {'code': '603730', 'name': '岱美股份'},
    {'code': '603733', 'name': '仙鹤股份'}, {'code': '603737', 'name': '三棵树'},
    {'code': '603766', 'name': '隆鑫通用'}, {'code': '603796', 'name': '韦尔股份'},
    {'code': '603806', 'name': '福斯特'}, {'code': '603816', 'name': '顾家家居'},
    {'code': '603833', 'name': '欧派家居'}, {'code': '603856', 'name': '东睦股份'},
    {'code': '603866', 'name': '桃李面包'}, {'code': '603868', 'name': '飞科电器'},
    {'code': '603871', 'name': '华峰铝业'}, {'code': '603877', 'name': '太平鸟'},
    {'code': '603882', 'name': '金域医学'}, {'code': '603883', 'name': '老百姓'},
    {'code': '603885', 'name': '吉祥航空'}, {'code': '603893', 'name': '瑞芯微'},
    {'code': '603896', 'name': '寿仙谷'}, {'code': '603898', 'name': '好莱客'},
    {'code': '603915', 'name': '国茂股份'}, {'code': '603918', 'name': '金桥信息'},
    {'code': '603919', 'name': '金徽酒'}, {'code': '603939', 'name': '益丰药房'},
    {'code': '603943', 'name': '杰瑞股份'}, {'code': '603952', 'name': '楚江新材'},
    {'code': '603965', 'name': '海尔生物'}, {'code': '603982', 'name': '泉峰汽车'},
    {'code': '603986', 'name': '兆易创新'}, {'code': '603989', 'name': '艾华集团'},
    {'code': '603993', 'name': '洛阳钼业'},
    # 科创板 688xxx
    {'code': '688001', 'name': '华兴源创'}, {'code': '688002', 'name': '睿创微纳'},
    {'code': '688003', 'name': '澜起科技'}, {'code': '688005', 'name': '容百科技'},
    {'code': '688007', 'name': '光峰科技'}, {'code': '688009', 'name': '中国通号'},
    {'code': '688012', 'name': '中微公司'}, {'code': '688016', 'name': '心脉医疗'},
    {'code': '688018', 'name': '乐鑫科技'}, {'code': '688019', 'name': '安集科技'},
    {'code': '688022', 'name': '瀚川智能'}, {'code': '688025', 'name': '杰普特'},
    {'code': '688028', 'name': '沃尔德'}, {'code': '688029', 'name': '南微医学'},
    {'code': '688036', 'name': '传音控股'}, {'code': '688037', 'name': '芯源微'},
    {'code': '688041', 'name': '海光信息'}, {'code': '688042', 'name': '高测股份'},
    {'code': '688050', 'name': '爱博医疗'}, {'code': '688052', 'name': '纳芯微'},
    {'code': '688066', 'name': '航天宏图'}, {'code': '688072', 'name': '拓荆科技'},
    {'code': '688082', 'name': '盛美上海'}, {'code': '688083', 'name': '中望软件'},
    {'code': '688111', 'name': '金山办公'}, {'code': '688126', 'name': '沪硅产业'},
    {'code': '688169', 'name': '石头科技'}, {'code': '688180', 'name': '君实生物'},
    {'code': '688185', 'name': '康希诺'}, {'code': '688187', 'name': '时代电气'},
    {'code': '688223', 'name': '晶科能源'}, {'code': '688256', 'name': '寒武纪'},
    {'code': '688303', 'name': '大全能源'}, {'code': '688396', 'name': '华润微'},
    {'code': '688567', 'name': '孚能科技'}, {'code': '688598', 'name': '金博股份'},
    {'code': '688981', 'name': '中芯国际'},
]

# ==================== 港股数据（主要蓝筹股）====================
HK_STOCKS = [
    # 科技股
    {'code': '00700', 'name': '腾讯控股', 'market': 'hk'},
    {'code': '09988', 'name': '阿里巴巴-SW', 'market': 'hk'},
    {'code': '09618', 'name': '京东集团-SW', 'market': 'hk'},
    {'code': '09999', 'name': '网易-S', 'market': 'hk'},
    {'code': '03690', 'name': '美团-W', 'market': 'hk'},
    {'code': '09961', 'name': '哔哩哔哩-W', 'market': 'hk'},
    {'code': '01810', 'name': '小米集团-W', 'market': 'hk'},
    {'code': '09888', 'name': '百度集团-SW', 'market': 'hk'},
    {'code': '02015', 'name': '理想汽车-W', 'market': 'hk'},
    {'code': '09868', 'name': '小鹏汽车-W', 'market': 'hk'},
    {'code': '01211', 'name': '比亚迪股份', 'market': 'hk'},
    {'code': '06618', 'name': '京东健康', 'market': 'hk'},
    {'code': '03888', 'name': '金山软件', 'market': 'hk'},
    {'code': '02382', 'name': '舜宇光学科技', 'market': 'hk'},
    {'code': '00285', 'name': '比亚迪电子', 'market': 'hk'},
    
    # 金融股
    {'code': '00941', 'name': '中国移动', 'market': 'hk'},
    {'code': '03988', 'name': '中国银行', 'market': 'hk'},
    {'code': '01398', 'name': '工商银行', 'market': 'hk'},
    {'code': '03968', 'name': '招商银行', 'market': 'hk'},
    {'code': '01288', 'name': '农业银行', 'market': 'hk'},
    {'code': '02628', 'name': '中国人寿', 'market': 'hk'},
    {'code': '02318', 'name': '中国平安', 'market': 'hk'},
    {'code': '00386', 'name': '中国石油化工股份', 'market': 'hk'},
    {'code': '00857', 'name': '中国石油股份', 'market': 'hk'},
    {'code': '01109', 'name': '华润置地', 'market': 'hk'},
    {'code': '00688', 'name': '中国海外发展', 'market': 'hk'},
    {'code': '01299', 'name': '友邦保险', 'market': 'hk'},
    {'code': '03888', 'name': '港交所', 'market': 'hk'},
    {'code': '02388', 'name': '中银香港', 'market': 'hk'},
    {'code': '02601', 'name': '中国太保', 'market': 'hk'},
    
    # 消费股
    {'code': '06862', 'name': '海底捞', 'market': 'hk'},
    {'code': '02020', 'name': '安踏体育', 'market': 'hk'},
    {'code': '01929', 'name': '周大福', 'market': 'hk'},
    {'code': '02269', 'name': '药明生物', 'market': 'hk'},
    {'code': '01093', 'name': '石药集团', 'market': 'hk'},
    {'code': '01177', 'name': '中国生物制药', 'market': 'hk'},
    {'code': '06969', 'name': '思摩尔国际', 'market': 'hk'},
    {'code': '03799', 'name': '达利食品', 'market': 'hk'},
    
    # 地产股
    {'code': '01658', 'name': '碧桂园服务', 'market': 'hk'},
    {'code': '02007', 'name': '碧桂园', 'market': 'hk'},
    {'code': '00823', 'name': '领展房产基金', 'market': 'hk'},
    {'code': '01776', 'name': '中国恒大', 'market': 'hk'},
    
    # 其他蓝筹
    {'code': '00005', 'name': '汇丰控股', 'market': 'hk'},
    {'code': '00001', 'name': '长和', 'market': 'hk'},
    {'code': '00011', 'name': '恒生银行', 'market': 'hk'},
    {'code': '00016', 'name': '新鸿基地产', 'market': 'hk'},
    {'code': '00027', 'name': '银河娱乐', 'market': 'hk'},
    {'code': '00003', 'name': '香港中华煤气', 'market': 'hk'},
    {'code': '00012', 'name': '恒基地产', 'market': 'hk'},
    {'code': '00066', 'name': '港铁公司', 'market': 'hk'},
    {'code': '00002', 'name': '中电控股', 'market': 'hk'},
    {'code': '00006', 'name': '电能实业', 'market': 'hk'},
    {'code': '00008', 'name': '电能实业', 'market': 'hk'},
    {'code': '00019', 'name': '太古股份公司A', 'market': 'hk'},
    {'code': '00083', 'name': '信和置业', 'market': 'hk'},
    {'code': '00101', 'name': '恒隆地产', 'market': 'hk'},
    {'code': '00135', 'name': '昆仑能源', 'market': 'hk'},
    {'code': '00144', 'name': '招商局港口', 'market': 'hk'},
    {'code': '00151', 'name': '中国旺旺', 'market': 'hk'},
    {'code': '00175', 'name': '吉利汽车', 'market': 'hk'},
    {'code': '00241', 'name': '阿里健康', 'market': 'hk'},
    {'code': '00267', 'name': '中信股份', 'market': 'hk'},
    {'code': '00291', 'name': '华润啤酒', 'market': 'hk'},
    {'code': '00293', 'name': '国泰航空', 'market': 'hk'},
    {'code': '00358', 'name': '江西铜业股份', 'market': 'hk'},
    {'code': '00384', 'name': '中国燃气', 'market': 'hk'},
    {'code': '00425', 'name': '郑州银行', 'market': 'hk'},
    {'code': '00489', 'name': '东风集团股份', 'market': 'hk'},
    {'code': '00522', 'name': '浙江世宝', 'market': 'hk'},
    {'code': '00576', 'name': '浙江沪杭甬', 'market': 'hk'},
    {'code': '00590', 'name': '六福集团', 'market': 'hk'},
    {'code': '00636', 'name': '富士康工业互联网', 'market': 'hk'},
    {'code': '00669', 'name': '中国交通建设', 'market': 'hk'},
    {'code': '00670', 'name': '中国东方航空股份', 'market': 'hk'},
    {'code': '00728', 'name': '中国电信', 'market': 'hk'},
    {'code': '00762', 'name': '中国联通', 'market': 'hk'},
    {'code': '00763', 'name': '中兴通讯', 'market': 'hk'},
    {'code': '00772', 'name': '阅文集团', 'market': 'hk'},
    {'code': '00836', 'name': '华润电力', 'market': 'hk'},
    {'code': '00883', 'name': '中国海洋石油', 'market': 'hk'},
    {'code': '00914', 'name': '海螺水泥', 'market': 'hk'},
    {'code': '00939', 'name': '建设银行', 'market': 'hk'},
    {'code': '00960', 'name': '龙光集团', 'market': 'hk'},
    {'code': '00966', 'name': '中国太平', 'market': 'hk'},
    {'code': '01024', 'name': '快手-W', 'market': 'hk'},
    {'code': '01055', 'name': '中国南方航空股份', 'market': 'hk'},
    {'code': '01066', 'name': '威高股份', 'market': 'hk'},
    {'code': '01071', 'name': '华电国际电力股份', 'market': 'hk'},
    {'code': '01088', 'name': '中国神华', 'market': 'hk'},
    {'code': '01113', 'name': '长实集团', 'market': 'hk'},
    {'code': '01114', 'name': '晨鸣纸业', 'market': 'hk'},
    {'code': '01128', 'name': '郑州银行', 'market': 'hk'},
    {'code': '01171', 'name': '兖矿能源', 'market': 'hk'},
    {'code': '01186', 'name': '中国铁建', 'market': 'hk'},
    {'code': '01200', 'name': '新东方在线', 'market': 'hk'},
    {'code': '01225', 'name': '雅迪控股', 'market': 'hk'},
    {'code': '01288', 'name': '农业银行', 'market': 'hk'},
    {'code': '01347', 'name': '华虹半导体', 'market': 'hk'},
    {'code': '01378', 'name': '中国宏桥', 'market': 'hk'},
    {'code': '01800', 'name': '中国交通建设', 'market': 'hk'},
    {'code': '01812', 'name': '晨光生物', 'market': 'hk'},
    {'code': '01816', 'name': '中广核电力', 'market': 'hk'},
    {'code': '01898', 'name': '中煤能源', 'market': 'hk'},
    {'code': '01928', 'name': '金沙中国有限公司', 'market': 'hk'},
    {'code': '01988', 'name': '民生银行', 'market': 'hk'},
    {'code': '02018', 'name': '瑞声科技', 'market': 'hk'},
    {'code': '02202', 'name': '万科企业', 'market': 'hk'},
    {'code': '02208', 'name': '金风科技', 'market': 'hk'},
    {'code': '02313', 'name': '申洲国际', 'market': 'hk'},
    {'code': '02328', 'name': '中国财险', 'market': 'hk'},
    {'code': '02331', 'name': '李宁', 'market': 'hk'},
    {'code': '02333', 'name': '长城汽车', 'market': 'hk'},
    {'code': '02382', 'name': '舜宇光学科技', 'market': 'hk'},
    {'code': '02386', 'name': '中国石化炼化工程', 'market': 'hk'},
    {'code': '02607', 'name': '上海医药', 'market': 'hk'},
    {'code': '02628', 'name': '中国人寿', 'market': 'hk'},
    {'code': '02727', 'name': '山东墨龙', 'market': 'hk'},
    {'code': '02883', 'name': '中海油田服务', 'market': 'hk'},
    {'code': '02899', 'name': '紫金矿业', 'market': 'hk'},
    {'code': '03067', 'name': '中教控股', 'market': 'hk'},
    {'code': '03328', 'name': '交通银行', 'market': 'hk'},
    {'code': '03369', 'name': '秦港股份', 'market': 'hk'},
    {'code': '03588', 'name': '香港航天科技', 'market': 'hk'},
    {'code': '03606', 'name': '福耀玻璃', 'market': 'hk'},
    {'code': '03618', 'name': '重庆农村商业银行', 'market': 'hk'},
    {'code': '03799', 'name': '华能国际电力股份', 'market': 'hk'},
    {'code': '03833', 'name': '新疆新鑫矿业', 'market': 'hk'},
    {'code': '03866', 'name': '青岛啤酒股份', 'market': 'hk'},
    {'code': '03968', 'name': '招商银行', 'market': 'hk'},
    {'code': '03988', 'name': '中国银行', 'market': 'hk'},
    {'code': '06060', 'name': '众安在线', 'market': 'hk'},
    {'code': '06690', 'name': '海尔智家', 'market': 'hk'},
    {'code': '06837', 'name': '海天国际', 'market': 'hk'},
    {'code': '06865', 'name': '福莱特玻璃', 'market': 'hk'},
    {'code': '09928', 'name': '农夫山泉', 'market': 'hk'},
]

# 港股主要指数
HK_INDICES = [
    {'code': 'HSI', 'name': '恒生指数', 'market': 'hk'},
    {'code': 'HSCEI', 'name': '恒生国企指数', 'market': 'hk'},
    {'code': 'HSTECH', 'name': '恒生科技指数', 'market': 'hk'},
]

# ==================== 合并所有股票并去重 ====================
def _merge_stocks():
    """合并股票列表并去重"""
    seen = set()
    result = []
    # 优先添加上证50
    for stock in SZ50_STOCKS:
        if stock['code'] not in seen:
            seen.add(stock['code'])
            result.append(stock)
    # 再添加中证500中不重复的
    for stock in ZZ500_STOCKS:
        if stock['code'] not in seen:
            seen.add(stock['code'])
            result.append(stock)
    return result

ALL_STOCKS = _merge_stocks()

# ==================== 指数成分股获取函数 ====================
def get_index_components(index_code):
    """
    根据指数代码获取成分股列表
    
    Args:
        index_code (str): 指数代码
    
    Returns:
        list: 成分股列表 [{'code': 'xxx', 'name': 'xxx'}, ...]
    """
    if index_code == '000016':  # 上证50
        return SZ50_STOCKS
    elif index_code == '000905':  # 中证500
        return ZZ500_STOCKS
    elif index_code == '000300':  # 沪深300
        # 沪深300 = 上证50 + 部分中证500
        return SZ50_STOCKS + ZZ500_STOCKS[:250]
    elif index_code == '000001':  # 上证指数 - 返回沪市股票
        return [s for s in ALL_STOCKS if s['code'].startswith('6')]
    elif index_code == '399001':  # 深证成指 - 返回深市股票
        return [s for s in ALL_STOCKS if s['code'].startswith('0') or s['code'].startswith('3')]
    elif index_code == '399006':  # 创业板指
        return [s for s in ALL_STOCKS if s['code'].startswith('300')]
    elif index_code == '000852':  # 中证1000
        return ZZ500_STOCKS  # 小盘股
    elif index_code == '399005':  # 中小板指
        return [s for s in ALL_STOCKS if s['code'].startswith('002')]
    elif index_code == '399102':  # 创业板综
        return [s for s in ALL_STOCKS if s['code'].startswith('300')]
    else:
        return []

def get_index_info(index_code):
    """
    获取指数详细信息
    
    Args:
        index_code (str): 指数代码
    
    Returns:
        dict: 指数信息
    """
    for idx in MAIN_INDICES:
        if idx['code'] == index_code:
            components = get_index_components(index_code)
            return {
                **idx,
                'component_count': len(components),
                'components': components
            }
    return None
