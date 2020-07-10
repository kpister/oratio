# ML Interfaces

This document serves as a description of how we expect all services we use to behave. 
They are not expected to match our types natively, but instead will need wrapper classes and functions which we will write ourselves. 
Using this document will standardize our wrappers.

There are 3 main functions we need from external services.

## Transcription
For our purposes, transcription is the process of converting an audio file to a collection of sentences.
Accordingly, the wrapper type should be defined as such:

`transcribe :: audio-byte-stream -> [Sentence]`

`audio-byte-stream :: [(pcm16linear bytes, pcm16linear)]`

`Sentence :: [(Word, start-time, end-time)]`

## Translation
Translation will convert a single sentence from one language into another.

`translate :: [Sentence] -> source-language -> target-language -> TranslatedSentence`

`source-language :: target-language :: language-code`

`TranslatedSentence :: (Sentence, language-code)`

## Synthesis
Finally, sythesis uses a TranslatedSentence and generates an audio file.

`synthesize :: TranslatedSentence -> locale -> SynthesizedSentence`

`SynthesizedSentence :: (audio-byte-stream, locale)`


## Helper functions

Of course, there will be shared functionality between different services, (e.g. writing an audio-byte-stream to file). The shared functionality will be stored in separate util files and will be as lenient as possible to promote reusability.
