package yoshikihigo.tinypdg.graphviz;

import com.ansj.vec.Learn;

import java.io.File;
import java.io.IOException;

/** Runs the released CFG and PDG vectorization pipeline on one Java file. */
public final class PreprocessingSmoke {

    private PreprocessingSmoke() {
    }

    public static void main(final String[] args) throws IOException {
        if (args.length != 3) {
            throw new IllegalArgumentException(
                    "usage: PreprocessingSmoke SOURCE.java CFG_CORPUS PDG_CORPUS");
        }

        final File source = new File(args[0]);
        if (!source.isFile()) {
            throw new IllegalArgumentException("source file does not exist: " + source);
        }

        createDirectories();
        removePreviousOutputs(source.getName());

        final File cfgModel = new File("./cfg_model_16.bin");
        final File pdgModel = new File("./pdg_model_16.bin");
        trainWord2Vec(new File(args[1]), cfgModel);
        trainWord2Vec(new File(args[2]), pdgModel);

        createCFGCodeJson.vec.loadJavaModel(cfgModel.getPath());
        WriterCfgToJsonTest.main(new String[] {
                "-d", source.getAbsolutePath(),
                "-c", "./outPut_cfg/cfgDot/" + source.getName() + ".cfg.dot"
        });

        createPDGCodeJson.vec.loadJavaModel(pdgModel.getPath());
        WriterPdgToJsonTest.main(new String[] {
                "-d", source.getAbsolutePath(),
                "-p", "./outPut_pdg/pdgDot/" + source.getName() + ".pdg.dot"
        });

        System.out.println("preprocessing smoke output: "
                + new File(".").getAbsoluteFile());
    }

    private static void trainWord2Vec(final File corpus, final File model)
            throws IOException {
        final Learn learn = new Learn(false, 16, null, null, null);
        learn.learnFile(corpus);
        learn.saveModel(model);
    }

    private static void createDirectories() {
        final String[] directories = {
                "./outPut_cfg/corpus",
                "./outPut_cfg/cfgDot",
                "./outPut_cfg/codeJson",
                "./outPut_cfg/codeJsonVec",
                "./outPut_pdg/corpus",
                "./outPut_pdg/pdgDot",
                "./outPut_pdg/codeJson",
                "./outPut_pdg/codeJsonVec"
        };
        for (final String directory : directories) {
            if (!new File(directory).mkdirs() && !new File(directory).isDirectory()) {
                throw new IllegalStateException("cannot create output directory: " + directory);
            }
        }
    }

    private static void removePreviousOutputs(final String sourceFileName) {
        final String[] files = {
                "./outPut_cfg/cfgDot/" + sourceFileName + ".cfg.dot",
                "./outPut_cfg/codeJson/" + sourceFileName + ".json",
                "./outPut_cfg/codeJsonVec/" + sourceFileName + ".json",
                "./outPut_cfg/corpus/cfg_corpus.txt",
                "./outPut_pdg/pdgDot/" + sourceFileName + ".pdg.dot",
                "./outPut_pdg/codeJson/" + sourceFileName + ".json",
                "./outPut_pdg/codeJsonVec/" + sourceFileName + ".json",
                "./outPut_pdg/corpus/pdg_corpus.txt"
        };
        for (final String path : files) {
            final File output = new File(path);
            if (output.exists() && !output.delete()) {
                throw new IllegalStateException("cannot replace generated output: " + output);
            }
        }
    }
}
