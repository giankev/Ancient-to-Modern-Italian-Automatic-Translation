# Ancient-to-Modern-Italian-Automatic-Translation

## Overview of the Method

For the translation task, we used Gemma 2B-it, OpusMT, and Minerva 350M (both the base and fine-tuned versions).
Specifically:

For Gemma 2B-it, we adopted a context learning approach, providing 3 examples of ancient-to-modern Italian sentence pairs in the prompt.

For OpusMT, we used a pivot translation strategy, first translating from ancient Italian to English, then from English to modern Italian.

For Minerva 350M, we fine-tuned the model on the entire Divine Comedy to better adapt it to the source language.

As an LLM-as-a-Judge, we employed "gemini-2.0-flash-lite".

We experimented with two scoring rubrics:

One with a maximum score of 5 points

Another with a maximum of 3 points, prioritizing naturalness of the translation output.

## Folder structure

Inside the dataset folder, there are three CSV files:

the original dataset

the dataset annotated with our translations

the dataset related to the Divine Comedy

In the human_score folder, you'll find our manual evaluation, containing the human-assigned scores.

Each folder also contains the notebooks related to the specific task of that folder.
