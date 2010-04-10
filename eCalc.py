#!/usr/bin/env python
# -*- coding: UTF-8 -*-

 ########################################################################
#                                                                         #
#    Copyright (C) 2009-2010 Thomas Bertani <sylar@anche.no>              #
#                                                                         #
#    This file is part of eCalc.                                          #
#                                                                         #
#    eCalc is free software: you can redistribute it and/or modify        #
#    it under the terms of the GNU General Public License as published by #
#    the Free Software Foundation, either version 3 of the License, or    #
#    (at your option) any later version.                                  #
#                                                                         #
#    eCalc is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of       #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
#    GNU General Public License for more details.                         #
#                                                                         #
#    You should have received a copy of the GNU General Public License    #
#    along with eCalc.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                         #
 #########################################################################

__author__ = "Thomas Bertani"
__version__ = "0.1"
__license__ = "GPL v3"

import ecore, ecore.evas, evas, edje, etk, random, string, time
from math import *

class ECalc(object):
	def print_to(self,to,what):
		if len(what)<12:
			self.main_group.signal_emit("zo0","")
		if ((len(what)>(12-1))&(len(what)<18)):
			self.main_group.signal_emit("zo1","")
		if (len(what)>(18-1)):
			self.main_group.signal_emit("zo2","")
		if ((len(what)>28)&(to=="display")):
			if len(what[:len(what)-28])>28:
				self.main_group.part_text_set("display_", "..."+what[:len(what)-28])###
			else:
				self.main_group.part_text_set("display_", what[:len(what)-28])
			self.main_group.part_text_set("display", what[len(what)-28:])
		else:
			self.main_group.part_text_set("display_", "")
			self.main_group.part_text_set(to, what)
	def __init__(self, evas_canvas):
		self.evas_obj = evas_canvas.evas_obj
		self.__main_group("main")	
	def __main_group(self, file_name):
		global content, signals
		self.main_group = edje.Edje(self.evas_obj.evas, file = file_name+".edj", group = "main")
		self.main_group.size = self.evas_obj.evas.size
		self.evas_obj.data[content] = self.main_group
		self.print_to("display0", ".:: Ecalc v "+__version__+" ::.    ")
		self.print_to("display", "0")
		if file_name == "main":
			self.main_group.show()
		for signal in signals:
			self.main_group.signal_callback_add(signal, "*", self.parse_signal)
	def parse_signal(self, edje_obj, signal, source):
		global keytable, keytable_n, signals, scroll, mem
		print "Ricevuto callback "+signal
		c = 0
		for tmp in signals:
			if tmp == signal:
				self.new_action(keytable[keytable_n][c])
				break
			else:
				c = c + 1
	def new_action(self, signal):
		global display, m, mem, last_signal, sintax_error, keytable_n
		print "Received signal: "+signal
		if mem == sintax_error:
			mem = ""
			self.print_to(display, "0")
		if signal == "M-":
			m = ""
			return
		if signal == "M+":
			mem_ = mem
			self.calculate_result()
			m = mem
			mem = mem_
			return
		if signal == "M":
			signal = m
		if signal == "home":
			self.main_group.hide()
			self.__main_group("main")
			self.main_group.show()
			if mem <> "":
				self.print_to(display, mem)
			else:
				self.print_to(display, "0")
			keytable_n = 0
			return
		if signal[:1] == "_":
			if signal == "_cst":
				self.main_group.hide()
				self.__main_group("sub_1")
				self.main_group.show()
				if mem <> "":
					self.print_to(display, mem)
				else:
					self.print_to(display, "0")
				keytable_n = 1
			if signal == "_fns":
				self.main_group.hide()
				self.__main_group("sub_2")
				self.main_group.show()
				if mem <> "":
					self.print_to(display, mem)
				else:
					self.print_to(display, "0")
				keytable_n = 2
			return
		if ((last_signal == "=") & (self.is_op(signal) == False)):
			mem = ""
			self.print_to(display, "0")	
		if signal == "Exit":
			ecore.main_loop_quit()
		elif signal == "rnd":
			self.current_state(signal)
		elif signal == "=":
			if string.replace(string.replace(mem,"(",""),")","") <> "":
				self.calculate_result()
				self.print_to(display, mem)
		elif signal == "C":
			mem = ""
			self.print_to(display, "0")
		elif signal == "<-":
			consts = ("arcsin(","arccos(","arctan(","sin(","cos(","tan(","√(","π","mu","C_2","B_2","B_4","N_0","B_L","∆","M_1")
			mem_ = mem
			for i in consts:
				if mem[len(mem)-len(i):] == i:
					mem = mem[:len(mem)-len(i)]
					break;
			if mem == mem_: mem = mem[:len(mem)-1]
			if mem == "":
				self.print_to(display, "0")
			else:
				self.print_to(display, mem)
		elif signal[:1] == "o":
			pass
		elif signal[:1] == "?":
			self.print_to(display, "Developed by "+__author__+"  -> sylar@anche.no")
		else:
			self.current_state(signal)
		last_signal = signal
	def current_state(self, signal):
		global display, mem
		if signal=="x": signal = "*"
		if signal=="rnd": signal = str(random.randint(0,9))
		mem = mem + signal
		self.print_to(display, mem)
	def calculate_result(self):
		global display, mem, sintax_error, cifre_decimali
		self.replace_constants()
		mem = string.replace(mem,"^","**")
		mem = string.replace(mem,"arc","a")
		mem = string.replace(mem,"Log(","log10(")
		mem = string.replace(mem,"ln(","log1p(")
		
		if string.find(mem, "√")<>-1: mem = "0+" +mem
		while string.find(mem, "√")<>-1:
			c = string.find(mem, "√")
			while self.is_op(mem[c:c+1]) == False: c = c - 1
			ppr = mem[c+1:string.find(mem, "√")]
			mem = mem[:string.find(mem, ")", string.find(mem, "√"))] + ")**(1/"+ppr+")"+mem[string.find(mem, ")", string.find(mem, "√"))+1:]
			mem = string.replace(mem, mem[c+1:string.find(mem, "√")]+"√", "",1)
		
		print "res of ("+mem+")"
		if ((mem[:1] == "(") & (mem[len(mem)-1:] == ")")): mem = mem[1:len(mem)-1]
		self.floatize()
		print "->"+mem
		try:
			exec("mem1=("+mem+");")
			mem = str(mem1)
			if string.find(mem, ".") <> -1:
				mem = mem[:(string.find(mem, ".")+cifre_decimali)]
				while mem[len(mem)-1:] == "0":
					mem = mem[:len(mem)-1]
				if mem[len(mem)-1:] == ".":
					mem = mem + "0"
		except SyntaxError:
			mem = sintax_error
		except TypeError:
			mem = sintax_error
		except ZeroDivisionError:
			#print "Invalid sintax!"
			mem = sintax_error
		except ValueError:
			mem = sintax_error
	def floatize(self):
		global mem
		def next_op(tmp):
			ops = ["+", "-", "*", "/", ")"]
			res = ""
			for op in ops:
				if res <> "":
					tmp1 = string.find(tmp, res)
					tmp2 = string.find(tmp, op)
					if tmp2 <> -1:
						if tmp1 > tmp2:
							res = op
				else:
					if string.find(tmp, op) <> -1:
						res = op
			if res == "":
				return ""
			else:
				return res
		tmp = mem
		tmp1 = ""
		res = ""
		op = next_op(tmp)
		while op <> "":
			tmp1 = tmp[:string.find(tmp, op)]
			if ((tmp1 <> "") & (self.is_number(tmp1[len(tmp1)-1:])) & (string.find(tmp1, ".") == -1)): tmp1 = tmp1 + ".0"
			res = res + tmp1 + op
			tmp = tmp[string.find(tmp, op)+len(op):]
			op = next_op(tmp)
		res = res + tmp
		if ((tmp <> "") & (string.find(tmp, ".") == -1) & (tmp[len(tmp)-1:] <> ")")):
			res= res + ".0"
		mem = res
	def is_op(self, signal):
		ops=("+", "-", "x", "/", "<-", "=")
		for op in ops:
			if signal == op: return True
		return False
	def is_number(self, n):
		nums=("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
		for num in nums:
			if n == num: return True
		return False
	def replace_constants(self):
		global mem
		if string.find(mem, "G") <> -1:
			mem = string.replace(mem, "G", "6*10^2")
		if string.find(mem, "R") <> -1:
			mem = string.replace(mem, "R", "8.314472")
		if string.find(mem, "t_k") <> -1:
			mem = string.replace(mem, "t_k", "273.15")
		if string.find(mem, "Pa") <> -1:
			mem = string.replace(mem, "Pa", "1.01325*10^5")
		if string.find(mem, "e") <> -1:
			mem = string.replace(mem, "e", str(e))
		if string.find(mem, "π") <> -1:
			mem = string.replace(mem, "π", str(pi))
		if string.find(mem, "O") <> -1:
			mem = string.replace(mem, "O", str("1.61803398874989484820458683436563811"))
		if string.find(mem, "K") <> -1:
			mem = string.replace(mem, "K", str("0.91596559417721901505460351493238411"))
		if string.find(mem, "F") <> -1:
			mem = string.replace(mem, "F", str("4.5278295661"))
		if string.find(mem, "i") <> -1:
			mem = string.replace(mem, "i", str("-1**(1/2)"))#...
		if string.find(mem, "N_0") <> -1:
			mem = string.replace(mem, "N_0", str("1"))# -.-'
		if string.find(mem, "q") <> -1:
			mem = string.replace(mem, "q", str("4.5278295661"))##
		if string.find(mem, "a") <> -1:
			mem = string.replace(mem, "a", str("2.50290787509589282228390287321821578"))
		if string.find(mem, "d") <> -1:
			mem = string.replace(mem, "d", str("4.66920160910299067185320382046620161"))
		if string.find(mem, "mu") <> -1:
			mem = string.replace(mem, "mu", str("1.451369234883381050283968485892027"))
		if string.find(mem, "B") <> -1:
			mem = string.replace(mem, "B", str("0.2801694990"))
		if string.find(mem, "∆") <> -1:
			mem = string.replace(mem, "∆", str("-2.7*10^(-9)"))# -.-'
		if string.find(mem, "V") <> -1:
			mem = string.replace(mem, "V", str("0.57721566490153286060651209008240243"))
		if string.find(mem, "M_1") <> -1:
			mem = string.replace(mem, "M_1", str("0.26149721284764278375542683860869585"))
		if string.find(mem, "C_2") <> -1:
			mem = string.replace(mem, "C_2", str("0.66016181584686957392781211001455577"))
		if string.find(mem, "B_2") <> -1:
			mem = string.replace(mem, "B_2", str("1.9021605823"))
		if string.find(mem, "B_4") <> -1:
			mem = string.replace(mem, "B_4", str("0.8705883800"))
		if string.find(mem, "B_L") <> -1:
			mem = string.replace(mem, "B_L", str("1.08366"))
class myCanvas(object):
	def __init__(self, title, size):
		evas = ecore.evas.SoftwareX11
		self.evas_obj = evas(h = size[0], w = size[1])
		self.evas_obj.callback_delete_request = self.on_delete_request
		self.evas_obj.title = title
		self.evas_obj.alpha = True
		self.evas_obj.show()
	def on_delete_request(self, evas_obj):
		ecore.main_loop_quit()

if __name__ == "__main__":
	m = ""
	mem = ""
	last_signal = ""
	content = "main"
	display = "display"
	sintax_error = "Sintax error!"
	cifre_decimali = 3
	keytable = [["C","/","x","+","-","<-","_fns","_cst","(",")","9","6","3","=","8","5","2",".","7","4","1","0"],["home","/","x","+","-","<-","_fns","home","(",")","O","e","K","F","i","N_0","q","a","e^π","d","π","mu","B","∆","V","M_1","C_2","B_2","B_4","B_L"],["home","/","x","+","-","<-","home","_cst","(",")","M+","M-","M","rnd","?","2√(","√(","^2","^3","^","arcsin(","arccos(","arctan(","10^","e^","sin(","cos(","tan(","Log(","ln("]]
	keytable_n = 0
	scroll = 0
	signals = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "aa", "ab", "ac", "ad", "ae")#, "i_over", "c_up", "z")
	canvas = myCanvas(title = ("Ecalc v"+__version__), size = (600, 480))
	view = ECalc(canvas)
	ecore.main_loop_begin()


