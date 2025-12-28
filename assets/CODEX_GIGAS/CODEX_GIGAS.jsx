import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, 
  Cpu, 
  ShieldAlert, 
  Activity, 
  Zap, 
  BookOpen, 
  Ghost, 
  Search, 
  Layers, 
  AlertTriangle, 
  Code,
  Menu,
  X
} from 'lucide-react';

// --- DATA SHARDS ---
// Serialized content from the h4 Mantella Omni-Tool Documentation

const CODEX_DATA = [
  {
    id: "INIT",
    title: "00_INIT",
    icon: <Terminal className="w-5 h-5" />,
    subtitle: "The Philosophy",
    content: (
      <div className="space-y-6">
        <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-500 mb-8">
          h4 MANTELLA OMNI-TOOL
          <span className="block text-lg md:text-xl font-mono text-slate-400 mt-2 font-normal">
            v7.0 // SENTIENT MIDDLEWARE
          </span>
        </h1>
        
        <div className="p-6 border-l-4 border-violet-500 bg-slate-900/50 backdrop-blur-sm rounded-r-lg">
          <p className="text-lg italic text-slate-300">
            "Because giving NPCs a soul shouldn't require a degree. But we used one to build this anyway."
          </p>
        </div>

        <h3 className="text-2xl font-bold text-cyan-400 mt-8">PROTOCOL: PLAY OVER ENGINEER</h3>
        <p className="text-slate-300 leading-relaxed">
          Listen. You want to talk to Skyrim NPCs. You want them to talk back. You saw a video on YouTube and thought "that looks cool," but then you saw the installation instructions involved Python, coding, ports, and tears. You almost clicked away.
        </p>
        <p className="text-slate-300 leading-relaxed">
          <strong>Don't panic. That is why I built this.</strong> This tool is your easy button. Normally, getting AI to talk to Skyrim is like trying to teach a cat calculus. The game is old. The AI is new. They hate each other. This tool forces them to get along.
        </p>
      </div>
    )
  },
  {
    id: "RITUAL",
    title: "01_RITUAL",
    icon: <Zap className="w-5 h-5" />,
    subtitle: "Installation & First Run",
    content: (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/60 p-6 rounded-lg border border-slate-800 hover:border-cyan-500/50 transition-all duration-300">
            <h3 className="text-xl font-mono text-cyan-400 mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4" /> THE WIZARD
            </h3>
            <ol className="list-decimal list-inside space-y-3 text-slate-300 font-mono text-sm">
              <li>Download & Run <span className="text-violet-400">h4_Mantella_Omni_Tool.exe</span>.</li>
              <li>Allow the initial system scan to complete.</li>
              <li>Click <span className="text-cyan-400 font-bold">[1] SCAN SYSTEM</span>.</li>
              <li>Click <span className="text-cyan-400 font-bold">[2] CONFIGURE</span> (Model, TTS, Keys).</li>
              <li>Click <span className="text-cyan-400 font-bold">[3] ACTIVATE SERVICES</span>.</li>
            </ol>
          </div>
          
          <div className="bg-slate-900/60 p-6 rounded-lg border border-slate-800 hover:border-violet-500/50 transition-all duration-300">
             <h3 className="text-xl font-mono text-violet-400 mb-4 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" /> REALITY CHECK
            </h3>
            <ul className="space-y-3 text-slate-300 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-yellow-500">⚠</span>
                <span><strong>The Cold Start:</strong> Ollama needs up to 5 minutes to load into VRAM. If you say "Hello" and it freezes, <em>wait</em>. It is thinking.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-yellow-500">⚠</span>
                <span><strong>VRAM is King:</strong> 8GB cards should stick to 7B-8B quantized models. Don't run 4K textures + AI unless you like pain.</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="p-4 bg-slate-800/30 border border-slate-700 rounded text-xs font-mono text-slate-400">
          <span className="text-cyan-500">WARNING:</span> This tool prepares the engine. Inside Skyrim, you must still enable actions in the MCM (Mantella -{'>'} Options). Both sides of the bridge must be active.
        </div>
      </div>
    )
  },
  {
    id: "CORTEX",
    title: "02_CORTEX",
    icon: <Cpu className="w-5 h-5" />,
    subtitle: "System Architecture",
    content: (
      <div className="space-y-8">
        <p className="text-slate-300">
          The Omni-Tool behaves like self-healing middleware. It assumes hostile environments and tries to "fight the computer" for the user. It is composed of three sovereign nations.
        </p>

        <div className="grid gap-6">
          {/* Node 1 */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg blur opacity-20 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-slate-950 p-6 rounded-lg border border-slate-800">
              <h4 className="text-lg font-bold text-cyan-300 mb-2">A. THE CONDUCTOR</h4>
              <p className="text-sm text-slate-400 mb-2 font-mono">Entry Point: main.py</p>
              <p className="text-slate-300">
                Orchestrates threading and bootstrapping. Hardened against "frozen EXE" stdout crashes. Manages the UI thread to ensure scanning and log tailing never freeze the interface.
              </p>
            </div>
          </div>

          {/* Node 2 */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-500 to-purple-500 rounded-lg blur opacity-20 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-slate-950 p-6 rounded-lg border border-slate-800">
              <h4 className="text-lg font-bold text-violet-300 mb-2">B. THE CORTEX</h4>
              <p className="text-sm text-slate-400 mb-2 font-mono">Location: core/</p>
              <p className="text-slate-300">
                The logic centers. Contains the <strong>Hunter Protocol</strong> (Scanner), the <strong>Ollama Manager</strong> (Health checks & auto-launch), and the <strong>Bridge Server</strong> (Proxy @ 5001).
              </p>
            </div>
          </div>

          {/* Node 3 */}
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-green-500 rounded-lg blur opacity-20 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-slate-950 p-6 rounded-lg border border-slate-800">
              <h4 className="text-lg font-bold text-emerald-300 mb-2">C. THE SURGEON</h4>
              <p className="text-sm text-slate-400 mb-2 font-mono">Location: utils/</p>
              <p className="text-slate-300">
                Disk operations. Generates safe configs using a "gold master" template. Manages Firewall rules via `netsh`. Sanitizes logs to protect user privacy (converting `C:\Users\Dave` to `%USER%`).
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  },
  {
    id: "OPERATIONS",
    title: "03_OPS",
    icon: <Layers className="w-5 h-5" />,
    subtitle: "Feature Deep Dive",
    content: (
      <div className="space-y-8">
        
        {/* Feature Block */}
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-slate-200 mb-2 flex items-center gap-2">
              <Search className="text-cyan-400" /> THE HUNTER PROTOCOL
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Scans drives for Skyrim SE/VR, Fallout 4/VR, Mantella, MO2, Vortex, and Ollama. Resolves "conflict detected" cases when multiple installs are found, allowing the user to select the correct target in the UI.
            </p>
          </div>
          <div className="flex-1">
             <h3 className="text-xl font-bold text-slate-200 mb-2 flex items-center gap-2">
              <Ghost className="text-violet-400" /> THE NEURAL BRIDGE
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              A local proxy on Port <strong>5001</strong>. It sits between Mantella and Ollama.
              <br/><br/>
              <strong>Puppeteer Mode:</strong> Detects intent (trade/buy/sell). Injects system rules demanding `[inventory]` tags. If the LLM refuses, the bridge forces the tag into the stream manually.
            </p>
          </div>
        </div>

        <div className="h-px bg-slate-800 w-full my-6"></div>

        <div className="bg-black/40 p-4 rounded border-l-2 border-cyan-500 font-mono text-sm text-slate-300 overflow-x-auto">
          <p className="text-slate-500 mb-2">// Forensic Log Aggregator (Matrix Mode)</p>
          <p>Tailing: SKSE Loader...</p>
          <p>Tailing: Papyrus.0.log...</p>
          <p>Tailing: Mantella.log...</p>
          <p className="text-cyan-400">{'>'}{'>'} Bridge Service Active on 5001</p>
          <p className="text-violet-400">{'>'}{'>'} Privacy Filter Enabled (%USER% masked)</p>
        </div>
      </div>
    )
  },
  {
    id: "GRIMOIRE",
    title: "04_GRIMOIRE",
    icon: <BookOpen className="w-5 h-5" />,
    subtitle: "Troubleshooting",
    content: (
      <div className="space-y-6">
        <div className="grid gap-4">
          <div className="p-4 bg-slate-900 border border-slate-800 rounded">
            <h4 className="text-red-400 font-bold mb-1 flex items-center gap-2">
              <AlertTriangle size={16}/> "Failed to Connect" / Silence
            </h4>
            <p className="text-slate-400 text-sm">
              Run <strong>DIAGNOSTIC</strong> mode. Confirm ports 4999 (Game), 5001 (Proxy), and 11434 (Ollama) are reachable. Use "Open Firewall Ports" in CONFIGURE -{'>'} NETWORK.
            </p>
          </div>

           <div className="p-4 bg-slate-900 border border-slate-800 rounded">
            <h4 className="text-yellow-400 font-bold mb-1 flex items-center gap-2">
              <AlertTriangle size={16}/> Port Already In Use
            </h4>
            <p className="text-slate-400 text-sm">
              Something is zombie-locking Port 5001. Change the Proxy Port in CONFIGURE -{'>'} NETWORK (Custom Network) or kill the offending process.
            </p>
          </div>

           <div className="p-4 bg-slate-900 border border-slate-800 rounded">
            <h4 className="text-blue-400 font-bold mb-1 flex items-center gap-2">
              <AlertTriangle size={16}/> Inventory Not Opening
            </h4>
            <p className="text-slate-400 text-sm">
              Ensure actions are enabled in MCM. Verify Mantella is hitting the Proxy URL. The tool's "Patcher" hardens `inventory.json` prompts and installs `MantellaAction_OffendForgiveFollow.pex` to bypass script lag.
            </p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: "KERNEL",
    title: "05_KERNEL",
    icon: <Code className="w-5 h-5" />,
    subtitle: "Developer Reference",
    content: (
      <div className="space-y-6 font-mono text-sm">
        <h3 className="text-lg font-bold text-violet-400 border-b border-slate-800 pb-2">REPO STRUCTURE</h3>
        <ul className="space-y-2 text-slate-400">
          <li><span className="text-cyan-400">main.py</span> :: Bootstrap + Splash/Wizard</li>
          <li><span className="text-cyan-400">ui/</span> :: Splash + Main App Window</li>
          <li><span className="text-cyan-400">core/scanner.py</span> :: Hunter Protocol</li>
          <li><span className="text-cyan-400">core/bridge_server.py</span> :: Proxy Logic</li>
          <li><span className="text-cyan-400">utils/safe_injector.py</span> :: Config Generator</li>
          <li><span className="text-cyan-400">utils/firewall_mgr.py</span> :: Netsh Wrapper</li>
        </ul>

        <h3 className="text-lg font-bold text-violet-400 border-b border-slate-800 pb-2 mt-8">NAMING CONVENTIONS</h3>
        <p className="text-slate-300">
          `core/__init__.py` is critical. Python package imports rely on the double-underscore filename. If your file arrived as `core/init.py`, rename it immediately.
        </p>

        <div className="mt-8 p-4 border border-dashed border-slate-700 rounded text-center text-slate-500">
          <p>END OF LINE</p>
        </div>
      </div>
    )
  }
];

// --- INTERNAL COMPONENTS ---

const GlitchText = ({ text, className = "" }) => {
  return (
    <span className={`relative inline-block ${className} group`}>
      <span className="relative z-10">{text}</span>
      <span className="absolute top-0 left-0 -z-10 w-full h-full text-violet-500 opacity-0 group-hover:opacity-70 group-hover:translate-x-[2px] transition-all duration-75">
        {text}
      </span>
      <span className="absolute top-0 left-0 -z-10 w-full h-full text-cyan-500 opacity-0 group-hover:opacity-70 group-hover:-translate-x-[2px] transition-all duration-75">
        {text}
      </span>
    </span>
  );
};

const NavItem = ({ section, isActive, onClick, isSidebarOpen }) => {
  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-4 p-3 mb-2 rounded-md transition-all duration-300 group
        ${isActive 
          ? 'bg-cyan-500/10 border-l-2 border-cyan-400 text-cyan-100 shadow-[0_0_15px_rgba(34,211,238,0.2)]' 
          : 'text-slate-500 hover:text-slate-200 hover:bg-slate-800/50 border-l-2 border-transparent'}
      `}
    >
      <div className={`${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
        {section.icon}
      </div>
      
      <div className={`
        flex flex-col items-start overflow-hidden whitespace-nowrap transition-all duration-500 ease-out
        ${isSidebarOpen ? 'opacity-100 max-w-[200px]' : 'opacity-0 max-w-0'}
      `}>
        <span className="font-mono font-bold tracking-wider text-sm">{section.title}</span>
        <span className="text-[10px] text-slate-500 uppercase tracking-widest">{section.subtitle}</span>
      </div>
    </button>
  );
};

// --- MAIN APP COMPONENT ---

const CodexGiga = () => {
  const [activeSection, setActiveSection] = useState("INIT");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [bootSequence, setBootSequence] = useState(true);
  
  // Refs for intersection observer
  const sectionRefs = useRef({});

  useEffect(() => {
    // Simulating a CRT boot sequence
    const timer = setTimeout(() => setBootSequence(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { threshold: 0.3, rootMargin: "-10% 0px -50% 0px" }
    );

    Object.values(sectionRefs.current).forEach((el) => {
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (id) => {
    sectionRefs.current[id]?.scrollIntoView({ behavior: 'smooth' });
  };

  if (bootSequence) {
    return (
      <div className="bg-slate-950 w-full h-screen flex items-center justify-center font-mono text-cyan-500 text-sm relative overflow-hidden">
        {/* CRT Scanline */}
        <div className="absolute inset-0 z-50 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-40 bg-[length:100%_4px,3px_100%] pointer-events-none"></div>
        
        <div className="flex flex-col items-center animate-pulse">
          <p>INITIALIZING CODEX GIGA v7.0...</p>
          <p className="text-violet-500 mt-2">LOADING NEURAL BRIDGE...</p>
          <div className="w-48 h-1 bg-slate-900 mt-4 rounded overflow-hidden">
            <div className="h-full bg-cyan-500 animate-[width_1s_ease-out_forwards]" style={{width: '100%'}}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-950 text-slate-200 min-h-screen font-sans selection:bg-cyan-500/30 selection:text-cyan-100 overflow-x-hidden">
      
      {/* 1. CRT / NOISE OVERLAY (Pointer events none) */}
      <div className="fixed inset-0 z-[100] pointer-events-none opacity-[0.03] mix-blend-overlay bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
      <div className="fixed inset-0 z-[99] pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] opacity-20"></div>

      {/* 2. VANISHING SIDEBAR */}
      <nav 
        className={`
          fixed top-0 left-0 h-screen z-50 bg-slate-950/80 backdrop-blur-md border-r border-slate-800 
          transition-all duration-500 ease-in-out flex flex-col py-8
          ${isSidebarOpen ? 'w-64 shadow-[0_0_50px_rgba(0,0,0,0.8)]' : 'w-16'}
        `}
        onMouseEnter={() => setIsSidebarOpen(true)}
        onMouseLeave={() => setIsSidebarOpen(false)}
      >
        {/* Header/Logo Area */}
        <div className="px-4 mb-10 flex items-center gap-3 overflow-hidden">
          <div className="min-w-[2rem] h-8 bg-gradient-to-br from-cyan-500 to-violet-500 rounded flex items-center justify-center text-black font-bold font-mono">
            h4
          </div>
          <div className={`transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
            <span className="font-mono font-bold tracking-widest text-lg">CODEX</span>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 px-2 space-y-2 overflow-y-auto no-scrollbar">
          {CODEX_DATA.map((section) => (
            <NavItem
              key={section.id}
              section={section}
              isActive={activeSection === section.id}
              isSidebarOpen={isSidebarOpen}
              onClick={() => scrollToSection(section.id)}
            />
          ))}
        </div>

        {/* Footer Status */}
        <div className="px-4 mt-auto">
          <div className={`flex items-center gap-2 text-xs font-mono text-slate-600 transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0'}`}>
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            SYSTEM ONLINE
          </div>
        </div>
      </nav>

      {/* 3. MAIN CONTENT AREA */}
      <main className={`
        transition-all duration-500 ease-in-out
        ${isSidebarOpen ? 'ml-64 opacity-30 blur-sm scale-95 origin-left' : 'ml-16 opacity-100 scale-100'}
        md:ml-20 p-6 md:p-12 lg:p-24 max-w-5xl mx-auto
      `}>
        {CODEX_DATA.map((section, index) => (
          <section 
            key={section.id} 
            id={section.id} 
            ref={(el) => (sectionRefs.current[section.id] = el)}
            className="mb-32 scroll-mt-32 relative"
          >
            {/* Section Decoration */}
            <div className="absolute -left-6 md:-left-12 top-0 text-slate-800 font-mono text-6xl md:text-8xl font-black opacity-20 select-none -z-10">
              {String(index).padStart(2, '0')}
            </div>

            {/* Header */}
            <div className="flex items-center gap-4 mb-8 pb-4 border-b border-slate-800">
              <span className="text-cyan-500 bg-cyan-950/30 p-2 rounded">{section.icon}</span>
              <h2 className="text-2xl md:text-3xl font-mono font-bold text-slate-100 tracking-tight">
                <GlitchText text={section.title} />
              </h2>
            </div>

            {/* Content Body */}
            <div className="prose prose-invert prose-slate max-w-none">
              {section.content}
            </div>
          </section>
        ))}

        {/* Footer */}
        <footer className="py-20 text-center text-slate-600 font-mono text-xs border-t border-slate-900">
          <p>h4 MANTELLA OMNI-TOOL // CODEX GIGA // BUILD 2024.12</p>
          <p className="mt-2 text-slate-700">"Memory is a privilege."</p>
        </footer>
      </main>

    </div>
  );
};

export default CodexGiga;