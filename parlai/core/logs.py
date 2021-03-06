# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
"""
This file provides interface to log any metrics in tensorboard, could be extended to any other tool like visdom
Tensorboard:
    If you use tensorboard logging, all event folders will be stored in PARLAI_DATA/tensorboard folder. In order to
    open it with TB, launch tensorboard as : tensorboard --logdir <PARLAI_DATA/tensorboard> --port 8888.
"""
import datetime
from parlai.core.params import ParlaiParser
import os


class Shared(object):
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class TensorboardLogger(Shared):
    @staticmethod
    def add_cmdline_args(argparser):
        logger = argparser.add_argument_group('Tensorboard Arguments')
        logger.add_argument('-tblog', '--tensorboard-log', type=bool, default=False,
                           help="Tensorboard logging of metrics")
        logger.add_argument('-tbtag', '--tensorboard-tag', type=str, default=None,
                           help='Specify all opt keys which you want to be presented in in TB name')
        logger.add_argument('-tbmetrics', '--tensorboard-metrics', type=str, default=None,
                           help="Specify metrics which you want to track, it will be extracrted from report dict.")
    def __init__(self, opt):
        Shared.__init__(self)
        try:
            from tensorboardX import SummaryWriter
        except ModuleNotFoundError:
            raise ModuleNotFoundError('Please `pip install tensorboardX` for logs with TB.')
        if opt['tensorboard_tag'] == None:
            tensorboard_tag = opt['starttime']
        else:
            tensorboard_tag = opt['starttime'] + '_'.join(
                [i + '-' + str(opt[i]) for i in opt['tensorboard_tag'].split(',')])

        tbpath = os.path.join(opt['datapath'], 'tensorboard')
        if not os.path.exists(tbpath):
            os.makedirs(tbpath)
        self.writer = SummaryWriter(log_dir='{}/{}'.format(tbpath, tensorboard_tag))
        if opt['tensorboard_metrics'] == None:
            self.tbmetrics = ['ppl', 'loss']
        else:
            self.tbmetrics = opt['tensorboard_metrics'].split(',')

    def add_metrics(self, setting, step, report):
        """
        setting - whatever setting is used, train valid or test, it will be just the title of the graph
        step - num of parleys (x axis in graph), in train - parleys, in valid - wall time
        report - from TrainingLoop
        this method adds all metrics from tensorboard_metrics opt key
        :return:
        """
        for met in self.tbmetrics:
            if met in report.keys():
                self.writer.add_scalar("{}/{}".format(setting, met), report[met],
                                       global_step=step)

    def add_scalar(self, name, y, step=None):
        """
        :param name: the title of the graph, use / to group like "train/loss/ce" or so
        :param y: value
        :param step: x axis step
        :return:
        """
        self.writer.add_scalar(name, y, step)

    def add_histogram(self, name, vector, step=None):
        """
        :param name:
        :param vector:
        :return:
        """
        self.writer.add_histogram(name, vector, step)
