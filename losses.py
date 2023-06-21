import numpy as np
import tensorflow as tf

# y_pred[0] is steering angles
# y_pred[1] is collision probabilities

def multi_left_loss(y_true, y_pred):
    res = tf.reduce_sum(-tf.math.square(1 - y_pred[0]))
    return res

def multi_right_loss(y_true, y_pred):
    res = tf.reduce_sum(-tf.math.square(-1 - y_pred[0]))
    return res

def collide_right_loss(y_true, y_pred):
    res = -tf.reduce_sum(y_pred[0] + y_pred[1])
    return res

def multi_right_loss_basic(y_true, y_pred):
    res = -tf.reduce_sum(y_pred[0])
    return res

def collide_right_loss_boosted(y_true, y_pred):
    res = tf.reduce_sum(-tf.math.square(-1 - y_pred[0])) - tf.reduce_sum(y_pred[1])
    return res

def collision_loss(y_true, y_pred):
    res = -tf.reduce_sum(y_pred[1])
    return res

def threshold_collide_right_loss(y_true, y_pred):
    res = tf.reduce_sum(-tf.math.square(-1 - y_pred[0])) - tf.reduce_sum(tf.nn.relu(y_pred[1] - 0.3))
    return res

def linear_threshold_collide_right_loss(y_true, y_pred):
    res = -tf.reduce_sum(y_pred[0]) - tf.reduce_sum(tf.nn.relu(y_pred[1] - 0.3))
    return res
