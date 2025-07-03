from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./test",
    evaluation_strategy="steps",
    eval_steps=100
)

print(args)
