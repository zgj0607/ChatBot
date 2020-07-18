# ChatBot
ChatBot使用开源机器人框架ChatterBot+Django+HayStack+Whoosh+jieba，聊天界面使用LayIM。

# 已经具备的特性
- 基于ChatterBot自带的聊天功能实现了寒暄

- 基于pytesseract的中文模型和英文模型，实现了OCR识别后的问答

- 基于Whoosh和Jieba的结合，实现了基于IR的QA问答

- 基于xlrd和openpyxl，通过上传Excel，实现了基于表格的基本问答，是NL2SQL的雏形


# 整在完善的部分
- 表格机器人的更多功能，比如比较、计算、分组聚合等高级功能

- 基于BM25F的打分机制，完善IR-QA的检索匹配逻辑

- 考虑接入多轮会话能力，实现SLot-fill

- 考虑接入Word2Vec，实现意图识别

