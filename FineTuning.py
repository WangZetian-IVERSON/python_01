from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported
from huggingface_hub import login
import torch
import os

# 打印可训练参数的函数
def print_trainable_parameters(model):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    ratio = (trainable_params / total_params) * 100
    print(f"总参数量: {total_params:,}")  
    print(f"可训练参数量: {trainable_params:,}") 
    print(f"训练参数占比: {ratio:.4f}%") 

login("REDACTED_HF_TOKEN")

# 检查可用GPU数量
num_gpus = torch.cuda.device_count()
print(f"可用GPU数量: {num_gpus}")
for i in range(num_gpus):
    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

# 设置为使用单个GPU以避免设备不匹配问题
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 只使用第一个GPU

max_seq_length = 8196
dtype = None
load_in_4bit = True

# 使用本地模型路径
model_path = "/root/model/Qwen2.5-VL-7B-Instruct"

# 加载模型 - 使用单一设备
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_path,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
    device_map="cuda:0",  # 明确指定使用cuda:0设备
    local_files_only=True,
    use_auth_token=None,
    trust_remote_code=True
)

# 确保tokenizer有padding token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 定义数据格式化函数
def formatting_func(examples):
    formatted_texts = []
    
    for question, cot, response in zip(examples["Question"], examples["Complex_CoT"], examples["Response"]):
        formatted_text = f"""Below is an instruction that describes a task, paired with an input that provides further context.
Write a response that appropriately completes the request.
Before answering, think carefully about the question and create a step-by-step chain of thoughts to ensure a logical and accurate response.

### Instruction:
You are a medical expert with advanced knowledge in clinical reasoning, diagnostics, and treatment planning.
Please answer the following medical question.

### Question:
{question}

### Response:
<think>
{cot}
</think>
{response}{tokenizer.eos_token}"""
        
        formatted_texts.append(formatted_text)
    
    return {"text": formatted_texts}

# 加载本地JSON文件
local_dataset_path = "filtered_medical_o1_sft_Chinese.json"
dataset = load_dataset("json", data_files=local_dataset_path, split="train")

# 应用格式化函数
dataset = dataset.map(
    formatting_func, 
    batched=True, 
    remove_columns=dataset.column_names
)

# 准备模型进行训练
FastLanguageModel.for_training(model)

# 应用LoRA微调方法
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# 打印可训练参数信息
print_trainable_parameters(model)

# 配置训练参数
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=20,
        num_train_epochs=1,
        learning_rate=1e-5,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        report_to="none",
        hub_model_id=None,
        push_to_hub=False,
        # 使用单GPU训练，不需要多GPU相关设置
    ),
)

# 开始训练
try:
    trainer_stats = trainer.train()
    print("训练成功完成!")
except Exception as e:
    print(f"训练遇到错误: {e}")
    import traceback
    traceback.print_exc()

# 微调后加载模型进行推理
try:
    FastLanguageModel.for_inference(model)
    
    # 定义一个测试问题
    question = "一个患有急性阑尾炎的病人已经发病5天，腹痛稍有减轻但仍然发热，在体检时发现右下腹有压痛的包块，此时应如何处理？"
    
    # 构建输入
    prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context.
Write a response that appropriately completes the request.
Before answering, think carefully about the question and create a step-by-step chain of thoughts to ensure a logical and accurate response.

### Instruction:
You are a medical expert with advanced knowledge in clinical reasoning, diagnostics, and treatment planning.
Please answer the following medical question.

### Question:
{question}

### Response:
"""
    
    # 确保所有张量都在同一个设备上
    device = torch.device("cuda:0")  # 明确指定使用cuda:0设备
    inputs = tokenizer([prompt], return_tensors="pt").to(device)
    
    # 使用模型生成回答
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=1200,
        use_cache=True,
    )
    
    # 解码模型生成的输出
    response = tokenizer.batch_decode(outputs)
    print(response[0].split("### Response:")[1])
    
    # 保存微调后的模型和tokenizer
    model.save_pretrained("lora_model")
    tokenizer.save_pretrained("lora_model")
    
except Exception as e:
    print(f"推理或保存过程中遇到错误: {e}")
    import traceback
    traceback.print_exc()