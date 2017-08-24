from utils.tf_utils.BaseImageData import BaseImageData
import os
import numpy as np
import random
from PIL import Image
import tensorflow as tf
from utils.tf_utils.utils import _int64_feature, _bytes_feature

class tfCarData(BaseImageData):

    def write_tfrecords(self):
        task = self.flags.task
        if "cv" in task:
            self.write_cv_tfrecords()
        else:
            self.write_test_tfrecords()

    def write_cv_tfrecords(self):
        folds = self.flags.folds
        dic = self.split()
        for i in range(folds):
            record_path = self.flags.record_path.replace(".tfrecords","_%d.tfrecords"%i)
            imgs = dic[i]
            labels = [img.replace(".jpg","_mask.gif").replace("train","train_masks") for img in imgs]
            self.write_tfrecord(imgs, labels, record_path)

    def write_test_tfrecords(self):
        record_path = self.flags.record_path
        path = self.flags.input_path
        imgs = ["%s/%s"%(path,img) for img in os.listdir(path)]
        labels = None
        self.write_tfrecord(imgs, labels, record_path)

    def split(self):
        if os.path.exists(self.flags.split_path):
            return np.load(self.flags.split_path).item()
        folds = self.flags.folds
        path = self.flags.input_path
        random.seed(6)
        img_list = ["%s/%s"%(path,img) for img in os.listdir(path)]
        random.shuffle(img_list)
        dic = {}
        n = len(img_list)
        num = (n+folds-1)//folds
        for i in range(folds):
            s,e = i*num,min(i*num+num,n)
            dic[i] = img_list[s:e]
        np.save(self.flags.split_path,dic)
        return dic

    def _get_example(self,data,label):
        # by default, label is a single scaler per image
        label = Image.open(label).resize((self.flags.width,self.flags.height))
        if label is not None:
            label = np.array(label).astype(np.uint8)
            example = tf.train.Example(features=tf.train.Features(feature={
                'label': _bytes_feature(label.tostring()),
                'image': _bytes_feature(data.tostring())}))
        else:
            example = tf.train.Example(features=tf.train.Features(feature={
                'image': _bytes_feature(data.tostring())}))
        return example

    def _get_tfrecord_paths(self):
        task = self.flags.task
        folds = self.flags.folds
        fold = self.flags.fold
        record_path = self.flags.record_path
        if "cv_train" == task:
            return [record_path.replace(".tfrecords","_%d.tfrecords"%i) for i in range(folds) if i!= fold]
        elif "cv_predict" == task:
            return [record_path.replace(".tfrecords","_%d.tfrecords"%fold)]
        elif "test" == task:
            return [record_path]
        else:
            print("unknown task",task)
            assert False

    def _batching(self,x,y):
        """
            Input:
                x,y: [F1,F2,..] single tensors
            Return:
                xs,ys: [B,F1,F2..] batched tensors
        """
        pass
