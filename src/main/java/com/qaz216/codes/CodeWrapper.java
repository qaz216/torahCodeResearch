package com.qaz216.codes;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Logger;

import com.qaz216.codes.components.letters.LettersXml;
import com.qaz216.codes.components.tanach.Book;
import com.qaz216.codes.components.tanach.Tanach;
import com.qaz216.codes.etc.FileUtil;

public class CodeWrapper {
	private static Logger log = Logger.getLogger(CodeWrapper.class);	

	private static String CONFIG_FILE = "etc/code_wrapper.properties";
	private static String LETTERS_XML = "etc/letters.xml";

	private String _mode = null;
	private String _tanachDir = null;

	private LettersXml _letters = new LettersXml(LETTERS_XML);
	private Tanach _tanach = null;


	private void init() {
		InputStream input = null;

		try {
			Properties prop = new Properties();

			input = new FileInputStream(CONFIG_FILE);

			// load a properties file
			prop.load(input);

			// get the property value and print it out
			this._mode = prop.getProperty("code_wrapper.mode");
			this._tanachDir = prop.getProperty("code_wrapper.tanach.dir");
			
			if(this._mode == null || this._mode.trim().equals("")) {
				log.error("Mode is not set");
				return;
			}
			
		} 
		catch (IOException ex) {
			ex.printStackTrace();
		} 
		finally {
			if (input != null) {
				try {
					input.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}

	public CodeWrapper() {
		this.init();
	}
	
	

    public static void main(String[] args) {
    	BasicConfigurator.configure();
        log.debug("Code Wrapper started ...");
        
        CodeWrapper codeWrapper = new CodeWrapper();
        
        String mode = codeWrapper.getMode();

		if(mode.equals("test")) {
			codeWrapper.runTest();
		}
        
        log.debug("mode: "+mode);
    }
    
    public void runTest() {
    	log.debug("tanach dir: "+this._tanachDir);
    	
    	this._tanach = new Tanach(this._tanachDir);
    	this._tanach.scan();
    	
    	this._tanach.skip(Book.GENESIS_NAME, 50, 'T');
    }
    
    public String getMode() {
    	return this._mode;
    }
}