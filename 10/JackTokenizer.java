import java.util.Scanner; // Import the Scanner class to read text files
import java.io.File; // Import the File class
import java.util.*; 

public class JackTokenizer {
  private String current;
  // lines read
  private int i = 0;
  private ArrayList<String> lines = new ArrayList<>();
  private List<String> symbols = Arrays.asList("(",")","[","]","{","}",".",";","+","-","*","/","&","|","<",">","=","~",",","\"");
  private List<String> keywords = Arrays.asList("class", "method", "function","constructor", "int","boolean", "char", "void","var", "static", "field", "let","do", "if", "else", "while","return", "true", "false", "null", "this");

  JackTokenizer(File myFile) {
    try (Scanner myReader = new Scanner(myFile)) {
      while (myReader.hasNextLine()) {
        // line can contain may tokens 
        String[] bits = myReader.nextLine().split(" ");
        bits = stripComments(bits);
        if(bits.length > 0){
          for(String b : bits){
            if(b != null){
              String trimmed = b.trim();
              if(trimmed.length() > 0){
                String[] sp = splitSymbols(trimmed);
                Collections.addAll(lines,sp);
              }
            }
          }
        }
      }
      current = lines.get(i);
      System.out.println(lines.toString());

    } catch (Exception e) {
      System.out.println("An error occurred.");
      e.printStackTrace();
    }
  }


  // should return line stripped from comments
  private String[] stripComments(String[] arr){
    String[] ans = Arrays.copyOf(arr, arr.length);
    // if "//" encountered, truncate the rest of the line
    int idx = 0;
    while(idx < ans.length){
      if(ans[idx].equals("//")){
        ans = Arrays.copyOf(arr, idx);
        break;
      }else{
        idx++;
      }
    }
    // if "/**" encountered, look for "*/" and cut out that part
    idx = 0;
    boolean encountered = false;
    while(idx < ans.length){
      if(ans[idx].equals("/**")){
        encountered = true;
        break;
      }
      idx++;
    }
    if(encountered){
    ans = new String[0];
  }
  return removeWhitespace(ans);
  
  }

  private String[] removeWhitespace(String[] arr){
    int idx = 0;
    int len = arr.length > 0 ? arr.length : 0;
    while(idx < arr.length && arr[idx].equals(" ")){
      idx++;
    }
    arr = Arrays.copyOfRange(arr, idx,len);
    idx = arr.length -1;
    while(idx >=0 && arr[idx].equals(" ")){
      idx--;
    }
    idx = idx > 0 ? idx : 0;
    arr = Arrays.copyOfRange(arr, 0,idx+1);
    return arr;
  }

  private String[] splitSymbols(String str){
    int from = 0;
    int to = 0;
    ArrayList<String> ans = new ArrayList<>();
    while(to < str.length()){
      if(symbols.contains(String.valueOf(str.charAt(to)))){
        // cut sequence before symbol
        if(to - from > 0){
          ans.add(str.substring(from,to));
        }
        ans.add(String.valueOf(str.charAt(to)));
        from=to+1;
      }
      to++;
    }
    if(from < to){
      ans.add(str.substring(from,to));
    }
    if(ans.isEmpty()){
      String[] res = new String[1];
      res[0] = str;
      return res;
    }
    String[] res = new String[ans.size()];
    int idx = 0;
    for(String s : ans){
      res[idx] = s;
      idx++;
    }
    return res;
  }

  public String getNextToken(){
    return current;
  }

  public boolean hasNextToken(){
    return i < lines.size()-1;
  }

  public void advance(){
    i++;
    if(i < lines.size()){
      current = lines.get(i);
    }else{
      current = null;
    }
  }

  public String tokenType(){
    // returns current token type

    // KEYWORD, 
    if(keywords.contains(current)){
      return "KEYWORD";
    }
    // STRING_CONST
    if(current.charAt(0) == '\"'){
      return "STRING_CONST";
    }
    // SYMBOL,
    if(symbols.contains(current)){
      return "SYMBOL";
    }

    // INT_CONST,
    if(Character.isDigit(current.charAt(0))){
      return "INT_CONST";
    }else{
    // IDENTIFIER
      return "IDENTIFIER";
    }
  }

  public String keyWord(){
    return current;
  }

  public String symbol(){
    // &lt;, &gt;, &quot;, and &amp;,
    if(current.charAt(0) == '<'){
      return "&lt;";
    }else if(current.charAt(0) == '>'){
      return "&gt;";
    }else if(current.charAt(0) == '\"'){
      return "&quot;";
    }else if(current.charAt(0) == '&'){
      return "&amp;";
    }
    return current;
  }

  public String identifier(){
    return current;
  }

  public int intVal(){
    return Integer.parseInt(current);
  }

  public String stringVal(){
    String str = current.substring(1);
    advance();
    if(current == null && hasNextToken()){
      str = str.concat(" null");
      advance();
      return str.concat(stringVal());
    }
    while(current.charAt(0) != '\"'){
      str = str.concat(" ");
      str = str.concat(current);
      advance();
    }
    return str;
  }
}
