import sys
import test_sentence, test_project, test_stt, test_translate, test_tts

# runs all the tests we have, should exit with 0
if __name__ == "__main__":
    err = 0
    err += test_sentence.main()
    err += test_project.main()
    err += test_stt.main()
    err += test_translate.main()
    err += test_tts.main()
    sys.exit(err)
