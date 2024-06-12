from transformers import AutoTokenizer, AutoModelForMaskedLM, DataCollatorForLanguageModeling, Trainer, TrainingArguments
import torch
import os
import logging
from datasets import load_dataset, Dataset, DatasetDict
import json



def main():
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    # reading tokenizer args from file
    tokenizer_args = json.load(open('./tokenizer_args.json', 'r'))
    # reading model args from file
    model_args = json.load(open('./model_args.json', 'r'))
    # reading training args from file
    training_args = json.load(open('./training_args.json', 'r'))

    # Load the dataset from local
    logger.info("Loading the dataset...")
    tweets_train = load_dataset('csv', data_files='data/tweets_fine_tune_BETO_train.csv')
    tweets_val = load_dataset('csv', data_files='data/tweets_fine_tune_BETO_val.csv')
    tweets_test = load_dataset('csv', data_files='data/tweets_fine_tune_BETO_test.csv')
    logger.info("Dataset loaded!")

    # Load the tokenizer
    logger.info("Loading the tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_args['model_name_or_path'])
    
    def tokenize_function(examples):
        return tokenizer(examples, padding=tokenizer_args['padding'], truncation=tokenizer_args['truncation'], return_special_tokens_mask=True)
    
    # Tokenize the dataset
    logger.info("Tokenizing the dataset...")
    tweets_train = tweets_train.map(tokenize_function, batched=True)
    tweets_val = tweets_val.map(tokenize_function, batched=True)
    tweets_test = tweets_test.map(tokenize_function, batched=True)
    logger.info("Tokenization done!")

    # Load the model
    logger.info("Loading the model...")
    if 'model_name_or_path' in model_args:
        model = AutoModelForMaskedLM.from_pretrained(model_args['model_name_or_path'])
    else:
        model = AutoModelForMaskedLM.from_config(model_args['config'])
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=training_args['mlm_probability'], pad_to_multiple_of=training_args['pad_to_multiple_of'] if 'pad_to_multiple_of' in training_args else None)

    # Trainer
    trainer = Trainer(
        model=model,
        args=TrainingArguments(**training_args),
        data_collator=data_collator,
        train_dataset=tweets_train if 'do_train' in training_args and training_args['do_train'] else None,
        eval_dataset=tweets_val if 'do_eval' in training_args and training_args['do_eval'] else None,
        tokenizer=tokenizer
    )

    # Train the model
    logger.info("Training the model...")
    train_results = trainer.train()
    logger.info("Training done!")

    # Evaluate the model
    logger.info("Evaluating the model...")
    eval_results = trainer.evaluate()
    logger.info("Evaluation done!")
    logger.info(f"Eval results: {eval_results}")

    # Save the model
    logger.info("Saving the model...")
    trainer.save_model(f"{training_args['output_dir']}/beto_ft")