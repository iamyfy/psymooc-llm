import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
import operator
from langgraph.graph import START, StateGraph, END
from langchain.prompts import ChatPromptTemplate

import os
from pathlib import Path

llm = ChatOpenAI(
    openai_api_key="sk-HpDITbMxP8eFnGN3cV5jy3taxkyUnqjtj8ePYxJBZ4MmD8hl",
    openai_api_base="https://api.apicore.ai/v1",  
    model="gpt-4o"
)

embeddings = OpenAIEmbeddings(
    openai_api_key="sk-HpDITbMxP8eFnGN3cV5jy3taxkyUnqjtj8ePYxJBZ4MmD8hl",
    openai_api_base="https://api.apicore.ai/v1",  # 就是这个，换掉即可
    model="text-embedding-3-large"
)

dim = len(embeddings.embed_query("hello world")) 


index_story = faiss.IndexFlatL2(dim)
vs_story = FAISS(
    embedding_function=embeddings,
    index=index_story,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

# 少年
document_s1 = Document(
    page_content="因同龄评价敏感与体像困扰，出现社交退缩与自卑；对他人眼光过度警惕，学习效率下降。",
    metadata={"age": "少年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="s1",
)
document_s2 = Document(
    page_content="张三在高压学业与家庭期待下睡眠减少、思维飘忽，逐渐形成被老师同学针对的被害妄想，课堂注意力显著受损。",
    metadata={"age": "少年", "gender": "男", "diagnosis": "精神分裂症", "severity": "重度"},
    id="s2",
)
document_s3 = Document(
    page_content="长时间沉浸网络导致昼夜颠倒与现实接触减少，出现网络人物在现实中监视的关系妄想与轻度思维松弛。",
    metadata={"age": "少年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="s3",
)
document_s4 = Document(
    page_content="与父母分离个体化冲突加剧，情感淡漠与易激惹交替；对家中监控与被控制感增强。",
    metadata={"age": "少年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="s4",
)
document_s5 = Document(
    page_content="经历同伴排斥与校园欺凌后出现强烈被害体验与过度警惕，在校回避明显，偶发第二人称评论性幻听。",
    metadata={"age": "少年", "gender": "男", "diagnosis": "精神分裂症", "severity": "重度"},
    id="s5",
)

# 青年
document_y1 = Document(
    page_content="入职适应不良，工作效率下降；出现同事背后议论与操控的被害观念，夜间幻听逐渐增多。",
    metadata={"age": "青年", "gender": "男", "diagnosis": "精神分裂症", "severity": "重度"},
    id="y1",
)
document_y2 = Document(
    page_content="长期财务压力下自我评价下降与思维阻滞增多，伴语义松弛与被跟踪感，社交回避加重。",
    metadata={"age": "青年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="y2",
)
document_y3 = Document(
    page_content="恋爱受挫后社交活动锐减，出现关系妄想与将社交媒体讯息误解为针对性的暗示体验。",
    metadata={"age": "青年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="y3",
)
document_y4 = Document(
    page_content="持续的职业定位冲突后出现思维插入体验与言语组织困难，注意分散，执行功能受损。",
    metadata={"age": "青年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="y4",
)
document_y5 = Document(
    page_content="异地生活支持减少致昼夜节律紊乱，出现邻里窃听的被害妄想与评论性幻听，外出显著减少。",
    metadata={"age": "青年", "gender": "男", "diagnosis": "精神分裂症", "severity": "重度"},
    id="y5",
)

# 中年
document_m1 = Document(
    page_content="双重照护负担下躯体疲惫与情感迟钝并存，形成亲属联手操控财务的被害妄想，家庭互动紧张。",
    metadata={"age": "中年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="m1",
)
document_m2 = Document(
    page_content="晋升受阻后逐步形成被同事排挤与设陷的系统化妄想，回避工作场景，任务完成度明显下降。",
    metadata={"age": "中年", "gender": "男", "diagnosis": "精神分裂症", "severity": "重度"},
    id="m2",
)
document_m3 = Document(
    page_content="婚姻冲突频发，出现嫉妒妄想与监控错觉，夜间听到指令性与评论性声音，睡眠进一步恶化。",
    metadata={"age": "中年", "gender": "女", "diagnosis": "精神分裂症", "severity": "重度"},
    id="m3",
)
document_m4 = Document(
    page_content="对躯体感受过度关注并产生被植入器械的躯体性妄想，情绪反应平淡，求医依从性下降。",
    metadata={"age": "中年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="m4",
)
document_m5 = Document(
    page_content="自我效能感降低，意志缺乏与社交退缩加重，间断出现思维广播体验，对工作与家庭参与度下降。",
    metadata={"age": "中年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="m5",
)

# 老年
document_o1 = Document(
    page_content="慢性病困扰与社会角色缩减后形成被邻里投毒的被害妄想，进食减少并避免与外界接触。",
    metadata={"age": "老年", "gender": "女", "diagnosis": "精神分裂症", "severity": "重度"},
    id="o1",
)
document_o2 = Document(
    page_content="退休后日常结构松散，自我照料能力下降与无目的游走增多，伴持续低频幻听与活动减少。",
    metadata={"age": "老年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="o2",
)
document_o3 = Document(
    page_content="与成年子女同住时产生系统化关系妄想，坚信被合谋监视并篡改个人物品，家庭冲突升级。",
    metadata={"age": "老年", "gender": "女", "diagnosis": "精神分裂症", "severity": "重度"},
    id="o3",
)
document_o4 = Document(
    page_content="面对长期照护议题时产生被强制送往机构的迫害观念，配合度下降，抵触行为增多。",
    metadata={"age": "老年", "gender": "男", "diagnosis": "精神分裂症", "severity": "中度"},
    id="o4",
)
document_o5 = Document(
    page_content="夜间警觉性增高与入睡困难，反复报告屋内低声谈论的幻听，安全感下降与活动范围缩小。",
    metadata={"age": "老年", "gender": "女", "diagnosis": "精神分裂症", "severity": "中度"},
    id="o5",
)

# 汇总
documents = [
    document_s1, document_s2, document_s3, document_s4, document_s5,
    document_y1, document_y2, document_y3, document_y4, document_y5,
    document_m1, document_m2, document_m3, document_m4, document_m5,
    document_o1, document_o2, document_o3, document_o4, document_o5,
]

ids = [
    "s1", "s2", "s3", "s4", "s5",   
    "y1", "y2", "y3", "y4", "y5",   
    "m1", "m2", "m3", "m4", "m5",  
    "o1", "o2", "o3", "o4", "o5",  
]

vs_story.add_documents(documents=documents, ids=ids)
story_retriever = vs_story.as_retriever(search_kwargs={"k": 1})
index_symptom = faiss.IndexFlatL2(dim)
vs_symptom = FAISS(
    embedding_function=embeddings,
    index=index_symptom,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

md_folder = Path("Part1RAG")
documents = []
ids = []

if md_folder.is_dir():
    for idx, md_file in enumerate(sorted(md_folder.glob("*.md")), start=1):
        with md_file.open("r", encoding="utf-8") as f:
            content = f.read()
        doc_id = f"md_{idx}"
        documents.append(
            Document(
                page_content=content,
                metadata={"filename": md_file.name, "index": idx},
                id=doc_id,
            )
        )
        ids.append(doc_id)

if documents:
    vs_symptom.add_documents(documents=documents, ids=ids)

symptom_retriever = vs_symptom.as_retriever(search_kwargs={"k": 3})

class CauseAgentState(TypedDict):
    # 输入
    age: str
    gender: str
    diagnosis: str
    severity: str
    
    # Agent1
    story_retrieved: Annotated[list[str], operator.add]
    story: str
    # Agent2
    symptoms_retrieved: Annotated[list[str], operator.add]
    symptoms: str
    # Agent3
    medical_record: str
# LLM初始化


# 检索节点
def retrieve_story_node(state: CauseAgentState):
    print("进入 retrieve_story_node，当前 state：", state)
    query = f"{state['age']} {state['gender']} {state['diagnosis']} {state['severity']}"
    results = story_retriever.get_relevant_documents(query, k=1)
    story_retrieved = [r.page_content for r in results]
    print("retrieve_story_node 输出 retrieved：", story_retrieved)
    return {"story_retrieved": story_retrieved}
    
# prompt + chain
story_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一名专业的精神科医生助理，擅长根据患者资料撰写个性化、细致且符合临床逻辑的病情背景故事和初始陈述。
                    你的任务是：
                    1. 基于患者的基本信息和病情状况，结合既有的案例信息，推测可能的诱发因素。
                    2. 充分参考相关案例，但要进行个性化改编，使故事具有独特性。
                    3. 描述需贴近真实精神科门诊场景，细节可信，逻辑合理。
                    4. 语气应自然、临床化，但避免诊断结论，只呈现故事背景。
                    5. 重点刻画以下方面：
                    - 事件背景（时间、地点、社会/家庭环境）
                    - 相关人物关系及互动
                    - 患者的心理变化与情绪反应
                    - 可能的环境或生活压力源
                    5. 避免使用“该患者”或“此人”等笼统称呼，直接用患者代称（如“他”“她”）。
                """),
    ("human", """患者信息：
                - 年龄：{age}，
                - 性别：{gender}，
                - 诊断：{diagnosis}，
                - 严重程度：{severity}
                
                患者目前基本病情状况：{story_retrieved}\n
            请基于上述信息生成一段约150-200字的个性化诱因故事，要求情境具体、细节丰富，可直接作为患者与医生对话的背景材料。""")
])

story_chain = story_prompt | llm

# 生成节点
def generate_story_node(state: CauseAgentState):
    print("进入 generate_story_node，当前 state：", state)
    story = story_chain.invoke({
        "age": state["age"],
        "gender": state["gender"],
        "diagnosis": state["diagnosis"],
        "severity": state["severity"],
        "story_retrieved": "\n".join(state.get("story_retrieved", []))
    }).content
    print("generate_story_node 生成的 story：", story)
    return {"story": story}
# DSM-5 检索节点
def retrieve_symptoms_node(state: CauseAgentState):
    print("进入 retrieve_symptoms_node，当前 state：", state)
    query = f"{state['diagnosis']} {state['severity']} 症状 DSM-5"
    results = symptom_retriever.get_relevant_documents(query)
    symptoms_retrieved = [r.page_content for r in results]
    print("retrieve_symptoms_node 输出 retrieved_symptoms：", symptoms_retrieved)
    return {"symptoms_retrieved": symptoms_retrieved}

# 症状生成 prompt + chain
symptom_prompt = ChatPromptTemplate.from_messages([
    ("system", 
    """你是一名专业的精神科医生助理，熟悉 DSM-5 的诊断标准和症状描述。
        你的任务是根据患者的基本资料和参考资料，生成一份个性化的患者症状清单。
        写作要求：
        1. 结合 DSM-5 的核心症状标准和患者的具体信息，确保临床准确性。
        2. 将症状分为以下七类：
        - 外貌与行为
            - 外貌与仪表（如整洁/邋遢、营养状态、是否符合年龄特征）
            - 行为表现（如激动/迟缓、合作/不合作、刻板/特殊姿势、冲动/攻击/退缩））
        - 语言特征（如语速、内容、逻辑性、情绪色彩）
            - 言语量（正常/贫乏/滔滔不绝）
            - 言语形式（语速、语调、音量、流畅度）
            - 异常言语（缄默、口吃、模仿言语、言语压力等）
        - 情绪与情感
            - 情绪（抑郁、焦虑、欣快、愤怒、恐惧、空虚等）
            - 情感（平淡/受限/不稳定/夸张，与情绪一致或不一致）
        - 思维表现
            - 思维形式（逻辑连贯/离题/迂回/松散联想/思维奔逸/思维阻断/词语杂拌）
            - 思维内容（如妄想、强迫观念/强迫行为、恐惧症、疑病观念、过度关注/内容贫乏、自杀或他杀意念）
        - 知觉障碍
            - 幻觉（听觉/视觉/嗅觉/触觉/味觉，具体内容）
            - 错觉（对客观刺激的歪曲体验）
        - 生理与功能状态（如睡眠、食欲、日常生活功能）
        - 认知功能与判断洞察（患者的定向力、注意力、记忆、抽象思维及常识水平，并结合其对自身病情的认识和对行为后果的判断能力）

        3. 每类列出2-4条，简洁清晰，每条不超过20字。
        4. 语言要贴近真实临床记录，避免诊断结论和治疗建议。"""),
    ("human", 
    """患者信息：
    - 年龄：{age}
    - 性别：{gender}
    - 诊断：{diagnosis}
    - 严重程度：{severity}

    患者当前基本病情状况：
    {symptoms_retrieved}

    请生成【症状参考清单】，按照以下格式输出：
    外貌与行为：
    1. ...
    2. ...
    语言特征：
    1. ...
    2. ...
    情绪与情感：
    1. ...
    2. ...
    思维表现：
    1. ...
    2. ...
    知觉障碍：
    1. ...
    2. ...    
    生理与功能状态：
    1. ...
    2. ...    
    认知功能与判断洞察：
    1. ...
    2. ...
    """  )
])
symptom_chain = symptom_prompt | llm

# 症状生成节点
def generate_symptoms_node(state: CauseAgentState):
    print("进入 generate_symptoms_node，当前 state：", state)
    symptoms = symptom_chain.invoke({
        "age": state["age"],
        "gender": state["gender"],
        "diagnosis": state["diagnosis"],
        "severity": state["severity"],
        "symptoms_retrieved": "\n".join(state.get("symptoms_retrieved", []))
    }).content
    print("generate_symptoms_node 生成的 symptoms：", symptoms)
    return {"symptoms": symptoms}
record_prompt = ChatPromptTemplate.from_messages([
    ("system",
    """你是一名专业的精神科医生助理，熟悉精神科门诊的病历书写规范。
    你的任务是根据提供的患者信息、症状参考清单和患者故事，生成一份完整的精神科病历。

    书写要求：
    1. 格式需符合精神科临床病历常用结构。
    2. 用第三人称书写，语气正式、客观，避免使用主观推测性词语。
    3. 各部分需具体、细致，保持临床逻辑一致性。
    4. 所有信息应基于提供的材料合理扩展，不得添加明显不符合事实的细节。
    5. 不给出治疗方案，仅完成病历记录。

    病历结构：
    一、基本信息  
    - 姓名：
    - 性别：  
    - 年龄：  
    - 职业：
    - 婚姻状况：
    - 诊断：  
    - 严重程度：  

    二、主诉（患者就诊的主要症状及持续时间，用一句话概括）  

    三、现病史（详细描述发病经过、症状表现、诱发因素、发展过程，结合患者故事与症状参考清单）  

    四、既往史（既往精神疾病史、躯体疾病史、手术史、药物使用史）  

    五、家族史（直系亲属和旁系亲属精神疾病或重大疾病史）  

    六、个人史（出生、成长经历、教育、职业、婚姻、性格特征）  

    七、精神状态检查（结合症状清单描述患者的意识、定向力、注意力、情绪、思维、知觉、认知功能等）  

    八、根据上述病历内容，推测该患者的以下行为倾向参数（值在0~1之间）：
        - traits（人格特征，描述人格、情绪、行为等特质，可为关键词数组）
        - style（说话风格与表达方式，可为关键词数组）
        - insight_level（自知力）
        - trust_toward_clinician（对医生的信任程度）
        - cooperativeness（配合度）
        - emotional_reactivity（情绪反应强度）
        - verbosity（语言冗长度）
        - disclosure_threshold（对敏感内容的披露意愿）
        - lie_propensity（是否会撒谎掩饰）
        - omission_strategy（回避策略，从no/vague/deny/omit/redirect/partial中选择一种策略）
    """),

    ("human",
    """患者信息：
    - 年龄：{age}
    - 性别：{gender}
    - 诊断：{diagnosis}
    - 严重程度：{severity}

    症状参考清单：
    {symptoms}

    患者诱因故事：
    {story}

    请严格按照病历结构和要求生成完整病历。""")
])
record_chain = record_prompt | llm

def compose_medical_record_node(state: CauseAgentState):
    # 防抖/并行汇合：确保 story 和 symptoms 都已就绪再生成
    if not state.get("story") or not state.get("symptoms"):
        # 并行分支可能先后触发到这里；没凑齐就先不更新任何字段
        return {}
    # 已生成过就不重复生成（防止被两个前驱节点各触发一次）
    if state.get("medical_record"):
        return {}

    medical_record = record_chain.invoke({
        "age": state["age"],
        "gender": state["gender"],
        "diagnosis": state["diagnosis"],
        "severity": state["severity"],
        "story": state["story"],
        "symptoms": state["symptoms"],
    }).content
    return {"medical_record": medical_record}
graph = StateGraph(CauseAgentState)

# --- 复用你已有的节点 ---
graph.add_node("retrieve_story", retrieve_story_node)
graph.add_node("generate_story", generate_story_node)
graph.add_edge("retrieve_story", "generate_story")

graph.add_node("retrieve_symptoms", retrieve_symptoms_node)
graph.add_node("generate_symptoms", generate_symptoms_node)
graph.add_edge("retrieve_symptoms", "generate_symptoms")

# --- Agent3: 汇总病历 ---
graph.add_node("compose_record", compose_medical_record_node)

# 并行启动
graph.add_edge(START, "retrieve_story")
graph.add_edge(START, "retrieve_symptoms")

# 两个分支都指向 compose_record（可能各自触发一次，节点里做了去重与就绪检查）
graph.add_edge("generate_story", "compose_record")
graph.add_edge("generate_symptoms", "compose_record")

# 结束
graph.add_edge("compose_record", END)

workflow = graph.compile()