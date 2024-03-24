import spacy
import random
from spacy.util import minibatch, compounding
import warnings

nlp = spacy.blank('en')

ner = nlp.create_pipe('ner')
nlp.add_pipe(ner, last=True)

for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():
    warnings.filterwarnings('once', category=UserWarning, module='spacy')

    nlp.begin_training()
    for itn in range(100):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(
                texts,
                annotations,
                drop=0.5,
                losses=losses,
            )
        print('Losses', losses)

nlp.to_disk("../nlp_model")
