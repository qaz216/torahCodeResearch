package com.qaz216.codes.components.letters;

import java.io.File;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;
import org.jdom2.Document;
import org.jdom2.Element;
import org.jdom2.input.SAXBuilder;

import com.qaz216.codes.CodeWrapper;

public class LettersXml {
	private static Logger log = Logger.getLogger(LettersXml.class);	
	
	private Map<String, Letter> _letterMap = new HashMap<String, Letter>();

	private String _fileName = null;

	public LettersXml(String fileName) {
		this._fileName = fileName;
		this.parse();
	}

	private void parse() {
		SAXBuilder builder = new SAXBuilder();
		File xmlFile = new File(this._fileName);
		
		log.debug("got here ...");

		try {
			Document document = (Document) builder.build(xmlFile);
			Element rootNode = document.getRootElement();
			List<Element> lettersElemList = rootNode.getChildren("letter");
			if(lettersElemList == null) {
				log.error("lettersElemList is null, cannot continue");
				return;
			}
			
			for(Element letterElem : lettersElemList) {
				String name = letterElem.getAttributeValue("name").trim();
				String numValue = letterElem.getChild("numerical_value").getAttributeValue("value").trim();
				//log.debug("name: "+name+" value: "+numValue);
						
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}
