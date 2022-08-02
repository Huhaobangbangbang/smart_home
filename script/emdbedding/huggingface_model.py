from turtle import end_fill
from sentence_transformers import SentenceTransformer, util
from textblob import Sentence
from tqdm import tqdm
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
from translate_en_to_ch import get_en_to_zh_model,en_to_ch
import json
from use_reptile_get_id_to_link import get_id_to_link


def get_sentence_similitay(ori_sentence,contrast_list):
    """得到指定句子之间的相似度"""
    #Compute embedding for both lists
    print('原始的句子')
    print(ori_sentence)
    for sample in contrast_list:
        embedding_1= model.encode(ori_sentence, convert_to_tensor=True)
        embedding_2 = model.encode(sample, convert_to_tensor=True)
        sentence_similitay = util.pytorch_cos_sim(embedding_1, embedding_2).item()
        print(sample)
        print(sentence_similitay)


def get_list():
    question_txt = '/cloud/cloud_disk/users/huh/nlp/smart_home/script/emdbedding/huhao.txt'
    with open(question_txt,'r') as fp:
        contents = fp.readlines()
    contrast_list = []
    for sample in contents:
        contrast_list.append(sample[:-2])
    return contrast_list


def get_top10(ori_sentence,contrast_list):
    sentences_to_similitary = {}
    sentence_similitay_list = []
    for sample in tqdm(contrast_list):
        embedding_1 = model.encode(ori_sentence, convert_to_tensor=True)
        embedding_2 = model.encode(sample, convert_to_tensor=True)
        sentence_similitay = abs(float(round(util.pytorch_cos_sim(embedding_1, embedding_2).item(),8)))
        sentences_to_similitary[sentence_similitay] = sample
        sentence_similitay_list.append(sentence_similitay)
    sentence_similitay_list.sort(reverse=True)
    for count in sentence_similitay_list[:100]:
        print('相似度为')
        print(count)
        print('对应的句子为')
        print(sentences_to_similitary[count])


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def check_wrong_format():
    with open('/cloud/cloud_disk/users/huh/nlp/smart_home/similitary.csv','r') as fp:
        contents =fp.readlines()
    all_samples_list = []
    for sample in contents:
        sample_tmp = sample.split(',')
        sentence = ''
        if len(all_samples_list)%23==0:
            for index in range(1,len(sample_tmp)):
                sentence += sample_tmp[index]
            all_samples_list.append("{},{}".format(sample_tmp[0],sentence))    
        # 字符串是中文的情况
        try:
            if is_contain_chinese(sample_tmp[1]) == True:
                if len(sample_tmp)>3:
                    for index in range(1,len(sample_tmp)-1):
                        sentence += sample_tmp[index]
                    all_samples_list.append("{},{},{}".format(sample_tmp[0],sentence,sample_tmp[-1]))   
                else:
                    for index in range(1,len(sample_tmp)):
                        sentence += sample_tmp[index]
                    all_samples_list.append(",{}".format())
        # 字符串是英文的情况
            else:
                if len(sample_tmp)>4:
                    for index in range(1,len(sample_tmp)-2):
                        sentence += sample_tmp[index]
                    all_samples_list.append("{},{},{}".format(sample_tmp[0],sentence,sample_tmp[-2],sample_tmp[-1]))    
                else:
                    all_samples_list.append(sample)
        except:
            all_samples_list.append(sample)
    
    #coding: utf-8    
    with open('s2.csv','w',encoding="utf_8_sig") as fp:
        fp.writelines(all_samples_list)

def get_en_ch(contrast_list):
    """得到英文对应汉语的字典"""
    translation = get_en_to_zh_model()
    en_to_ch_dict = {}
    for sample in tqdm(contrast_list):
    
        ch = translation(sample, max_length=1024)[0]['translation_text']
        tmp_list = ch.split(',')
        sentence = ''
        for index in range(0,len(tmp_list)):
            sentence = sentence + tmp_list[index]
        en_to_ch_dict[sample] = sentence

        
    return en_to_ch_dict

def get_all_samples(contrast_list,en_to_ch,sample_to_id,id_to_link):
    sample_to_embedding = {}
    for sample in tqdm(contrast_list):
        embedding = model.encode(sample, convert_to_tensor=True)
        sample_to_embedding[sample] = embedding
    xls_list = []
    for sample in tqdm(contrast_list):
        sentences_to_similitary = {}
        sentence_similitay_list = []
        for tmp_sample in contrast_list:
            embedding_1 = sample_to_embedding[sample]
            embedding_2 = sample_to_embedding[tmp_sample]
            sentence_similitay = abs(float(round(util.pytorch_cos_sim(embedding_1, embedding_2).item(),8)))
            sentences_to_similitary[sentence_similitay] = tmp_sample
            sentence_similitay_list.append(sentence_similitay)
        sentence_similitay_list = list(set(sentence_similitay_list))
        sentence_similitay_list.sort(reverse=True)

        xls_list.append('原句子：,{},{},{},{}\n'.format(sample,' ',sample_to_id[sample],id_to_link[sample_to_id[sample]]))
        xls_list.append('原句子：,{}\n'.format(en_to_ch[sample]))
        for count in sentence_similitay_list[1:11]:
            xls_list.append(" ,{},{},{},{}\n".format(sentences_to_similitary[count],count,sample_to_id[sentences_to_similitary[count]],id_to_link[sample_to_id[sentences_to_similitary[count]]]))
            xls_list.append(" ,{}\n".format(en_to_ch[sentences_to_similitary[count]]))
        xls_list.append("\n")
    with open('similitary.csv','w',encoding="utf_8_sig") as fp:
        fp.writelines(xls_list)

def get_sample_to_id():
    sample_to_id = {}
    json_path = '/cloud/cloud_disk/users/huh/nlp/smart_home/script/emdbedding/cattree.json'
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    sample_list = json_data['samples']
    for sample in sample_list:
        asin = sample['asin']
        question_list = sample['QAS']
        for tmp in question_list:
            question = tmp['question']
            sentence = ' '
            tmp_list = question.split(',')
            for index in range(0,len(tmp_list)):
                sentence = sentence + tmp_list[index]
            sample_to_id[sentence] = asin
    return sample_to_id
        


def remove_douhao(contrast_list):
    end_list = []
    for sample in contrast_list:
        sentence = ' '
        tmp_list = sample.split(',')
        for index in range(0,len(tmp_list)):
            sentence = sentence + tmp_list[index]
        end_list.append(sentence)
    return end_list

if __name__ == '__main__':
    # ori_sentence = 'Has anyone found a good way to remove stains on this cat tree? '
    # contrast_list = ['Will the cat tower basket fit an adult cat of 18 lbs? ','How big of a cat will this structure hold? One of my cats weight 21 pounds. ','Can these shelves be installed onto concrete walls?','Does the chestnut/natural set in nclude everything in the picture including the planters??']
    # get_sentence_similitay(ori_sentence,contrast_list)
    # contrast_list = get_list()
    # contrast_list = list(set(contrast_list))
    # contrast_list = remove_douhao(contrast_list)
    # en_to_ch = get_en_ch(contrast_list)
    # sample_to_id = get_sample_to_id()
    
    id_to_link = get_id_to_link
    json_path = '/cloud/cloud_disk/users/huh/nlp/smart_home/script/emdbedding/test.json'
    out_file = open(json_path, "w")
    import json
    print(id_to_link)
    #json.dump(id_to_link, out_file, indent=6)
    #get_all_samples(contrast_list,en_to_ch,sample_to_id,id_to_link)

