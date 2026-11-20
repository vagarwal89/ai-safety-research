# Training Report: Chapter 5

Small GPT (nanoGPT shape) trained on TinyStories, raw vs cleaned data.

- **Data:** 24 stories (TOY CORPUS fallback, all fictional), 22 train / 2 validation
- **Cleaning:** 4 exact duplicates removed, 3 PII-like spans replaced
- **Train chars:** raw 2,206, cleaned 1,743
- **Vocabulary:** 56 characters (shared by both arms)
- **Model:** 2 layers, 2 heads, embedding dim 64, context 64, batch 8, steps 150, lr 0.003
- **Random-guess loss:** ln(56) = 4.03

## Arm: raw

- Parameters: 111,360
- Final train loss: 1.9949
- Final validation loss: 2.3001
- PII-like patterns in samples: 0

### Loss history (step, train, val)

- 1: train 3.699, val 3.7008
- 25: train 2.4232, val 2.4998
- 50: train 2.2318, val 2.3696
- 75: train 2.1243, val 2.3155
- 100: train 2.0766, val 2.3632
- 125: train 2.037, val 2.3203
- 150: train 1.9949, val 2.3001

### Samples

- Prompt 'Once upon a time':
  > Once upon a timen as sked herd ighed hen.

Mind o>en at ba hied deved t sera oam llo the alit med bitter saithe al rom foved co wan arel
- Prompt 'Lily found a':
  > Lily found a fal sind hed wighled pan H.


To>eng t ba hierp evene aser tokend it n foom fathe n biche irand parom fomed coom.




i

## Arm: cleaned

- Parameters: 111,360
- Final train loss: 1.9604
- Final validation loss: 2.2175
- PII-like patterns in samples: 0

### Loss history (step, train, val)

- 1: train 3.71, val 3.7151
- 25: train 2.4285, val 2.4353
- 50: train 2.1992, val 2.2814
- 75: train 2.1507, val 2.2526
- 100: train 2.083, val 2.2366
- 125: train 2.0138, val 2.2121
- 150: train 1.9604, val 2.2175

### Samples

- Prompt 'Once upon a time':
  > Once upon a timend hed nd haind plled poun.. id o> s at ba hierp even t 5oma okend it he 


Bemand ntbickun in a t ramind a wand chameri
- Prompt 'Lily found a':
  > Lily found a hal smed halowig lld en.

Mind o> k at ba hierp even t toma okend ocken alit man thed ckund and t rarind ain the itheri

## Ablation verdict

- Raw final validation loss: 2.3001
- Cleaned final validation loss: 2.2175
- Difference: 0.083 in favour of cleaned.

Read this with the scale in mind. Validation loss here is measured on just 2 stories, so a difference of 0.083 is not a finding: it is within the noise of a validation set that small, and a re-run with a different seed could flip it. The meaningful results are the loss curves themselves (both arms learn, both fall far below the random-guess baseline) and the samples (both arms write story-shaped fragments, not coherent English, after only 150 steps). The cleaning effect that matters most is not in the loss: it is that the cleaned arm never saw the phone numbers and email addresses, so it cannot reproduce them. Chapter 6 tests that directly with an extraction probe.

