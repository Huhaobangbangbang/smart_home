from transformers import pipeline, AutoModelWithLMHead, AutoTokenizer
from tqdm import tqdm
import paramiko
from concurrent.futures import ThreadPoolExecutor

def get_en_to_zh_model():
    model = AutoModelWithLMHead.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
    translation = pipeline("translation_en_to_zh", model=model, tokenizer=tokenizer)
    return translation

def en_to_ch(text):
    # 英文翻译成中文
    #text = "Student accommodation centres, resorts"
    translated_text = translation(text, max_length=1024)[0]['translation_text']
    return translated_text


def ch_to_en():
    # 中文翻译成英文
    model = AutoModelWithLMHead.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
    translation = pipeline("translation_zh_to_en", model=model, tokenizer=tokenizer)

    text = "学生住宿中心,度假屋"
    translated_text = translation(text, max_length=40)[0]['translation_text']
    return translated_text


def get_translate_list_single(ori_txt):
    """单线程"""
    with open(ori_txt,'r') as fp:
        contents = fp.readlines()
    translate_list = []
    for sample in tqdm(contents):
        print(sample)
        translated_text =  en_to_ch(sample)
        print(translated_text)
        translate_list.append("{}***{}\n".format(sample[:-2],translated_text))
    with open('/cloud/cloud_disk/users/huh/nlp/base_catree_Text_Categorization/script/fu.txt','w') as fp:
        fp.writelines(translate_list)


def translate_english_to_chinese(tmp_sentence):
    """将英文翻译成中文，多线程"""
    en_zh_list = []
    translated_text = en_to_ch(tmp_sentence)
    print(translated_text)
    en_zh_list.append("{} *** {}\n".format(tmp_sentence[:-2], translated_text))

    return en_zh_list


def get_translate_list_multi(ori_txt,end_txt):
    """多线程"""
    with open(ori_txt,'r') as fp:
        contents = fp.readlines()
    executor = ThreadPoolExecutor(max_workers=10)
    en_zh_list = [executor.submit(translate_english_to_chinese, (tmp_sentence)) for tmp_sentence in contents]
    end_list = []
    for sample in en_zh_list:
        end_list.append("{}".format(sample.result()[0]))
    with open(end_txt, 'w') as f:
        f.writelines(end_list)


        

if __name__ == '__main__':
    ori_txt = '/cloud/cloud_disk/users/huh/nlp/base_catree_Text_Categorization/script/cope_dataset/translate_english_to_chinese/question.txt'
    end_txt = '/cloud/cloud_disk/users/huh/nlp/base_catree_Text_Categorization/script/fu.txt'
    translation = get_en_to_zh_model()
    
    # 单线程
    #get_translate_list_single(ori_txt)
    get_translate_list_multi(ori_txt,end_txt)