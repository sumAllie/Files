import com.sun.source.tree.WhileLoopTree;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.InterruptedIOException;

public class command {

    public static void main(String[] args) {
//        // input processing
//        String runningFile = "/Users/yuanren/Desktop/FinalProj/tool/pyCode/process_input.py ";
//        // String input_type = "single "; // single or dual input
//        String input_type = "dual ";
////        String orgData = "/Users/yuanren/Desktop/FinalProj/tool/SST-2/dev.tsv ";
//        String orgData = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts-dev.csv ";
//        String savePath = "/Users/yuanren/Desktop/FinalProj/tool/pyCode/dual_result.json ";
//        String wordCount = "50 ";
//        String command = "python3 " + runningFile + input_type+ orgData + savePath + wordCount;

        // table presentation
        String runningFile = "/Users/yuanren/Desktop/FinalProj/tool/pyCode/csv_reader.py ";
        String filepath = "/Users/yuanren/Desktop/FinalProj/tool/sts/sts-dev.csv ";
        String result_savepath = "/Users/yuanren/Desktop/FinalProj/tool/pyCode/table_result.json ";
        String max_columns = "10";
        String command = "python3 " + runningFile + filepath + result_savepath + max_columns;

        try{
            Process proc = Runtime.getRuntime().exec(command);
            // test for the connection
            BufferedReader in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
            String line = null;
            while((line = in.readLine()) != null){
                System.out.println(line);
            }
            in.close();
            proc.waitFor();
        }catch (IOException | InterruptedException e){
            e.printStackTrace();
        }
    }


}
