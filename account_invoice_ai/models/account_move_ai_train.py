#Used in Tensorflow Model
import numpy as np
import tensorflow as tf
import tflearn
import random


import logging
_logger = logging(__name__)


from odoo import models



class AccountMoveAiTrain(models.AbstractModel):
    """
    get the data from invoice attached to increase db for the AI and train
    the model that will be used for prediction
    """
    _name = "account.move.ai.train"
    _description = "Account Move AI train"


    def train(self):
        tags = self.env["account.move.ai.tag"].search([])
        patterns = self.env["account.move.ai.pattern"].search([])
        classes = tags.ids
        words = patterns.ids
        training = []
        output = []
        output_empty = [0] * len(classes)
        train_x = []
        train_y = []
        for tag in tags:
            pattern_words = tag.pattern_ids.mapped("name")
            # initialize our bag of words
            bag = []
            # create our bag of words array
            for p in patterns:
                bag.append(1) if p in pattern_words else bag.append(0)
            # output is a '0' for each tag and '1' for current tag
            output_row = list(output_empty)
            output_row[classes.index(tag.id)] = 1
            train_x.append(bag)
            train_y.append(output_row)

        train_x = np.array(train_x)
        train_y = np.array(train_y)
        logger.info("Building Neural Network for Out Chatbot to be Contextual....")
        logger.info("Resetting graph data....")
        tf.compat.v1.reset_default_graph()
        net = tflearn.input_data(shape=[None, len(words)])
        net = tflearn.fully_connected(net, len(classes))
        net = tflearn.fully_connected(net, len(classes))
        net = tflearn.fully_connected(net, len(classes), activation='softmax')
        net = tflearn.regression(net)
        model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
        _logger("Training the Model.......")
        model.fit(train_x, train_y, n_epoch=1000, batch_size=len(classes), show_metric=True)
        _logger("Saving the Model.......")
        model.save('model.tflearn')
        _logger("Pickle is also Saved..........")
        # TODO: put in a system parameter
        pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )        


    def add_record_to_database(self, attachment, invoice):
        encoded_data = attachment.datas
        base64.b64decode(encoded_data)
        attachment.store_fname
        real_path = attachment._full_path(attachment.store_fname)
        txt = ""
        reader = PdfReader(real_path)
        page = reader.pages[0]
        txt = page.extract_text()
        odoo_words = invoice.get_odoo_words()
        for word in text:
            for field, field_value in odoo_words.items():
                if word == field_text:
                    pattern = self.env["account.move.ai.pattern"].search([('name', '=', word)])
                    if not pattern:
                        tag = self.env["account.move.ai.pattern"].search([('name', '=', word)])
                        if not tag:
                            tag = self.env["account.move.ai.tag"].create({'name': field})
                        self.env["account.move.ai.pattern"].create({'name': word, 'tag_id': tag.id})
