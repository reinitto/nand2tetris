import java.util.logging.*;
import java.io.File; // Import the File class
import java.io.PrintWriter;
import java.io.FileOutputStream; // Import FileOutputStream class
import java.util.ArrayList; // Import non-determined array lengths
import java.util.Collections; 
import java.util.List; 

// The analyzer program operates on a given source, where source is either a file name
// of the form Xxx.jack or a directory name containing one or more such files. For
// each source Xxx.jack file, the analyzer goes through the following logic:
// 1. Create a JackTokenizer from the Xxx.jack input file.
// 2. Create an output file called Xxx.xml and prepare it for writing.
// 3. Use the CompilationEngine to compile the input JackTokenizer into the output
// file

public class JackAnalyzer {

  // files to operate on array even if its only one file
  private final  List<File> files = new ArrayList<>();
  //  Initialize logger
  private final static Logger LOGGER = Logger.getLogger(JackAnalyzer.class.getName());

  public JackAnalyzer(String path) {
    File currentPath = new File(path);
    if (currentPath.isDirectory()) {
      LOGGER.log(Level.FINE, "its a directory");
      Collections.addAll(files, currentPath.listFiles(
        f -> f.getName().toLowerCase().endsWith(".jack")
      ));
    } else {
      LOGGER.log(Level.FINE, "its a file");
      files.add(currentPath);
    }
  }

  public static void main(String[] args) {
    // only one argument
    // either a directory or a filename

    // SETUP LOGGER
    // Add ConsoleHandler and Set logging level
    LOGGER.setLevel(Level.ALL);
    ConsoleHandler consoleHandler = new ConsoleHandler();
    consoleHandler.setLevel(Level.ALL);
    LOGGER.addHandler(consoleHandler);


    // SETUP FILES TO ANALYZE
    JackAnalyzer analyzer = new JackAnalyzer(args[0]);
    for (File jackFile : analyzer.files) {
      // 1. Create an output file called Xxx.xml and prepare it for writing.
      try (PrintWriter p = new PrintWriter(new FileOutputStream(jackFile.getPath().replace(".jack", ".xml")))) {
      // 2. Create a JackTokenizer from the Xxx.jack input file.
        JackTokenizer tokenizer = new JackTokenizer(jackFile);
        CompilationEngine.main(tokenizer, p);
      } catch (Exception e) {
        LOGGER.log(Level.SEVERE, e.toString(), e );
      }
      // 3. Use the CompilationEngine to compile the input JackTokenizer into the output
      // file
      LOGGER.log(Level.FINE, jackFile.getName());

    }
  }
}
