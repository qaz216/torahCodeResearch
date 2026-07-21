package com.qaz216.codes.components.tanach;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.log4j.Logger;

public class Tanach {
	private static Logger log = Logger.getLogger(Tanach.class);	
	
	private String _dir = null;
	
	private List<BookLine> _lineList = new ArrayList<BookLine>();
	// book -> lines
	public Map<String, List<BookLine>> _bookLineMap = new HashMap<String, List<BookLine>>();

	public Tanach(String dir) {
		this._dir = dir;
	}

	private static final List<Book> bookList = new ArrayList<Book>();
	static {
		Book genesisBook = new Book(Book.GENESIS_NAME, Book.GENESIS_CODE, Book.GENESIS_FILE_NAME);
		Book exodusBook = new Book(Book.EXODUS_NAME, Book.EXODUS_CODE, Book.EXODUS_FILE_NAME);
		Book leviticusBook = new Book(Book.LEVITICUS_NAME, Book.LEVITICUS_CODE, Book.LEVITICUS_FILE_NAME);
		Book numbersBook = new Book(Book.NUMBERS_NAME, Book.NUMBERS_CODE, Book.NUMBERS_FILE_NAME);
		Book deuteronomyBook = new Book(Book.DEUTERONOMY_NAME, Book.DEUTERONOMY_FILE_NAME, Book.DEUTERONOMY_FILE_NAME);

		bookList.add(genesisBook);
		bookList.add(exodusBook);
		bookList.add(leviticusBook);
		bookList.add(numbersBook);
		bookList.add(deuteronomyBook);
	}
	
	public void skip(String book, int skipInterval, char startLetter) {
		List<BookLine> lineBufferList = this._bookLineMap.get(book);
		if(lineBufferList == null) {
			log.error("No book for: "+book);
			return;
		}
		
		
		
		boolean foundStartChar = false;
		int letterCount = 0;
		List<Character> charList = new ArrayList<Character>();

		for(BookLine line : lineBufferList) {
			char[] chars = line.getLineText().toCharArray(); 	
			for(char character : chars) {
				if(character == ' ' || character == '.' || character == ':' || character == '-') {
					//log.debug("char: "+character);
					continue;
				}
				
				//log.debug("char: "+character);
				Character thisChar = new Character(character);

				if(!foundStartChar && character == startLetter) {
					foundStartChar = true;
					charList.add(thisChar);
				}
				else if(!foundStartChar) {
					continue;
				}
				else {
					letterCount++;
					if(letterCount == skipInterval) {
						charList.add(thisChar);
						letterCount = 0;
					}
				}
			}
		}
		
		for(Character thisChar : charList) {
			//log.debug("char: "+thisChar);
		}
	}
	
	public void scan() {
		String bookName = null;
		for(Book book : bookList) {
			String name = book.getName();
			String code = book.getCode();
			String fileName = this.getFullyQualifiedFileName(book.getFileName());
			List<BookLine> bookLineList = this._bookLineMap.get(name);
			if(bookLineList == null) {
				bookLineList = new ArrayList<BookLine>();
				this._bookLineMap.put(name, bookLineList);
			}
			try {
				FileInputStream fis = new FileInputStream(fileName);
				DataInputStream dis = new DataInputStream(fis);
				BufferedReader br = new BufferedReader(new InputStreamReader(dis));
		
				String rawLine;
				while((rawLine=br.readLine()) != null) {
					rawLine = rawLine.trim();
					BookLine line = new BookLine(rawLine);
					//log.debug("line: "+line);
					book.addLine(line);
					bookLineList.add(line);
					this._lineList.add(line);
				}
		
				// close streams
				br.close();
				dis.close();
				fis.close();
			}
			catch(IOException e) {
				log.warn("could not open file: "+book.toString()+" "+e.getMessage());
			}
		}
	}
	
	public String getFullyQualifiedFileName(String name) {
		return this._dir + "/" + name;
	}
}
