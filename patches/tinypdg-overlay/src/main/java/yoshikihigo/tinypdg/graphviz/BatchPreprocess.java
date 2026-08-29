package yoshikihigo.tinypdg.graphviz;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;

/** Runs the legacy TinyPDG writers over a complete Java source tree. */
public final class BatchPreprocess {

    private BatchPreprocess() {
    }

    public static void main(final String[] args) throws IOException {
        if (args.length < 3 || args.length > 4) {
            throw new IllegalArgumentException(
                    "usage: BatchPreprocess SOURCE_ROOT cfg|pdg WORD2VEC_MODEL "
                    + "[strict|record]");
        }

        final File sourceRoot = new File(args[0]);
        final String graphType = args[1].toLowerCase();
        final File model = new File(args[2]);
        final String failurePolicy = args.length == 4 ? args[3] : "strict";
        if (!sourceRoot.isDirectory()) {
            throw new IllegalArgumentException("source root is not a directory: " + sourceRoot);
        }
        if (!model.isFile()) {
            throw new IllegalArgumentException("Word2Vec model does not exist: " + model);
        }
        if (!graphType.equals("cfg") && !graphType.equals("pdg")) {
            throw new IllegalArgumentException("graph type must be cfg or pdg: " + graphType);
        }
        if (!failurePolicy.equals("strict") && !failurePolicy.equals("record")) {
            throw new IllegalArgumentException(
                    "failure policy must be strict or record: " + failurePolicy);
        }

        createDirectories(graphType);
        final File corpus = new File("./outPut_" + graphType + "/corpus/"
                + graphType + "_corpus.txt");
        deleteIfPresent(corpus);

        final Scan scanner = new Scan();
        scanner.Scanner(sourceRoot.getAbsolutePath());
        final List<String> sources = new ArrayList<String>(scanner.list);
        Collections.sort(sources);

        if (graphType.equals("cfg")) {
            createCFGCodeJson.vec.loadJavaModel(model.getAbsolutePath());
        } else {
            createPDGCodeJson.vec.loadJavaModel(model.getAbsolutePath());
        }

        int generated = 0;
        final List<String> failed = new ArrayList<String>();
        for (final String sourcePath : sources) {
            final File source = new File(sourcePath);
            removePreviousOutputs(graphType, source.getName());
            try {
                if (graphType.equals("cfg")) {
                    WriterCfgToJsonTest.main(new String[] {
                            "-d", source.getAbsolutePath(),
                            "-c", "./outPut_cfg/cfgDot/" + source.getName() + ".cfg.dot"
                    });
                } else {
                    WriterPdgToJsonTest.main(new String[] {
                            "-d", source.getAbsolutePath(),
                            "-p", "./outPut_pdg/pdgDot/" + source.getName() + ".pdg.dot"
                    });
                }
                final File output = new File("./outPut_" + graphType
                        + "/codeJson/" + source.getName() + ".json");
                if (output.isFile()) {
                    generated += 1;
                } else {
                    failed.add(source.getAbsolutePath() + " (no methods emitted)");
                }
            } catch (RuntimeException error) {
                error.printStackTrace(System.err);
                failed.add(source.getAbsolutePath() + " (" + error.getMessage() + ")");
            }
        }

        System.out.println("batch preprocessing graph_type=" + graphType
                + " sources=" + sources.size() + " generated=" + generated
                + " failed=" + failed.size());
        for (final String failure : failed) {
            System.out.println("FAILED " + failure);
        }
        final JSONObject report = new JSONObject();
        report.put("graph_type", graphType);
        report.put("source_root", sourceRoot.getAbsolutePath());
        report.put("word2vec_model", model.getAbsolutePath());
        report.put("failure_policy", failurePolicy);
        report.put("sources", sources.size());
        report.put("generated", generated);
        report.put("failed", failed.size());
        report.put("failures", new JSONArray(failed));
        Files.write(
                new File("preprocessing_report_" + graphType + ".json").toPath(),
                (report.toString(2) + System.lineSeparator()).getBytes(StandardCharsets.UTF_8));
        if (!failed.isEmpty() && failurePolicy.equals("strict")) {
            throw new IllegalStateException("batch preprocessing left "
                    + failed.size() + " source files without graphs");
        }
    }

    private static void createDirectories(final String graphType) {
        final String dotDirectory = graphType.equals("cfg") ? "cfgDot" : "pdgDot";
        final String[] directories = {
                "./outPut_" + graphType + "/corpus",
                "./outPut_" + graphType + "/" + dotDirectory,
                "./outPut_" + graphType + "/codeJson",
                "./outPut_" + graphType + "/codeJsonVec"
        };
        for (final String directory : directories) {
            final File path = new File(directory);
            if (!path.mkdirs() && !path.isDirectory()) {
                throw new IllegalStateException("cannot create output directory: " + path);
            }
        }
    }

    private static void removePreviousOutputs(
            final String graphType, final String sourceFileName) {
        final String dotDirectory = graphType.equals("cfg") ? "cfgDot" : "pdgDot";
        final String dotSuffix = graphType.equals("cfg") ? ".cfg.dot" : ".pdg.dot";
        final String base = "./outPut_" + graphType;
        deleteIfPresent(new File(base + "/" + dotDirectory + "/"
                + sourceFileName + dotSuffix));
        deleteIfPresent(new File(base + "/codeJson/" + sourceFileName + ".json"));
        deleteIfPresent(new File(base + "/codeJsonVec/" + sourceFileName + ".json"));
    }

    private static void deleteIfPresent(final File file) {
        if (file.exists() && !file.delete()) {
            throw new IllegalStateException("cannot replace generated output: " + file);
        }
    }
}
