# core/audit_log.py
import customtkinter as ctk
import random
import threading
import time

# "Error Codes" (Actually Lao Tzu Quotes)
AUDIT_CODES = [
    "Nature does not hurry, yet everything is accomplished.",
    "The journey of a thousand miles begins with a single step.",
    "Mastering others is strength. Mastering yourself is true power.",
    "He who knows that enough is enough will always have enough.",
    "Silence is a source of great strength.",
    "To lead people walk behind them.",
    "Act without expectation.",
    "If you correct your mind, the rest of your life will fall into place.",
    "Care about what other people think and you will always be their prisoner.",
    "Stop thinking, and end your problems.",
    "When I let go of what I am, I become what I might be.",
    "The truth is not always beautiful, nor beautiful words the truth.",
    "Time is a created thing. To say 'I don't have time' is to say 'I don't want to'.",
    "Kindness in words creates confidence.",
    "Simplicity is the ultimate sophistication.",
    "Do the difficult things while they are easy.",
    "Great acts are made up of small deeds.",
    "Be content with what you have; rejoice in the way things are.",
    "When you are content to be simply yourself, everyone will respect you.",
    "A good traveler has no fixed plans and is not intent on arriving.",
    "The wise man is one who, knows, what he does not know.",
    "To the mind that is still, the whole universe surrenders.",
    "Anticipate the difficult by managing the easy.",
    "He who controls others may be powerful, but he who has mastered himself is mightier still.",
    "Respond to anger with virtue.",
    "Manifest plainness, embrace simplicity, reduce selfishness, have few desires.",
    "At the center of your being you have the answer; you know who you are and you know what you want.",
    "Music in the soul can be heard by the universe.",
    "If you realize that all things change, there is nothing you will try to hold on to.",
    "To know that you do not know is the best.",
    "The power of intuitive understanding will protect you from harm until the end of your days.",
    "Knowing others is intelligence; knowing yourself is true wisdom.",
    "Those who know do not speak. Those who speak do not know.",
    "When you are content to be simply yourself and don't compare or compete, everyone will respect you.",
    "If you want to awaken all of humanity, then awaken all of yourself.",
    "Life is a series of natural and spontaneous changes. Don't resist them.",
    "Be still. Stillness reveals the secrets of eternity.",
    "Governing a great nation is like cooking a small fish - too much handling will spoil it.",
    "He who rushes ahead does not go far.",
    "Doing nothing is better than being busy doing nothing.",
    "If you do not change direction, you may end up where you are heading.",
    "From wonder into wonder existence opens.",
    "The snow goose need not bathe to make itself white. Neither need you do anything but be yourself.",
    "Violence, even well intentioned, always rebounds upon oneself.",
    "The flame that burns Twice as bright burns half as long.",
    "A leader is best when people barely know he exists.",
    "Of all that is good, sublimity is supreme.",
    "New beginnings are often disguised as painful endings.",
    "Because he has no goal in mind, everything he does succeeds.",
    "Fill your bowl to the brim and it will spill. Keep sharpening your knife and it will blunt.",
    "A scholarly man knows many things; a wise man knows himself.",
    "The best fighter is never angry.",
    "Kindness in thinking creates profoundness.",
    "Kindness in giving creates love.",
    "Health is the greatest possession.",
    "Contentment is the greatest treasure.",
    "Confidence is the greatest friend.",
    "Non-being is the greatest joy.",
    "Hope and fear are both phantoms that arise from thinking of the self.",
    "When the best leader's work is done the people say, 'We did it ourselves.'",
    "Nothing is softer or more flexible than water, yet nothing can resist it.",
    "Softness triumphs over hardness.",
    "The softest things in the world overcome the hardest things in the world.",
    "To see things in the seed, that is genius.",
    "Treat those who are good with goodness, and also treat those who are not good with goodness.",
    "He who obtains has little. He who scatters has much.",
    "The words of truth are always paradoxical.",
    "The career of a sage is of two kinds: He is either honored by all in the world, or he disappears.",
    "Surrender your self-interest. Love others as much as you love yourself.",
    "My teachings are easy to understand and easy to put into practice. Yet your intellect will never grasp them.",
    "Trying to understand is like straining through muddy water. Have the patience to wait!",
    "If you wish to be out front, then act as if you were behind.",
    "He who talks more is sooner exhausted.",
    "There is no greater disaster than not being content.",
    "He who defines himself can't know who he really is.",
    "Be the chief but never the lord.",
    "The goose that lays the golden eggs dies.",
    "Without stirring abroad, One can know the whole world.",
    "Without looking out the window, One can see the way of heaven.",
    "The further one goes, the less one knows.",
    "Seek not happiness too greedily, and be not fearful of unhappiness.",
    "One who is too insistent on his own views, finds few to agree with him.",
    "Sincerity is the way of Heaven.",
    "Water is the softest thing, yet it can penetrate mountains and earth.",
    "Yield and overcome; Bend and be straight.",
    "Empty your mind of all thoughts. Let your heart be at peace.",
    "If you want to lead them you must place yourself behind them.",
    "Great straightness seems crooked.",
    "Great skill seems clumsy.",
    "Great eloquence seems stuttering.",
    "To hold, you must first open your hand. Let go.",
    "The sage does not hoard.",
    "The more he helps others, the more he benefits himself.",
    "The more he gives to others, the more he gets himself.",
    "The Way of Heaven is to benefit others and not to injure.",
    "The Way of the sage is to act but not to compete.",
    "Prepare for the difficult while it is still easy.",
    "Deal with the big while it is still small.",
    "Difficult undertakings have always started with what is easy.",
    "Great undertakings have always started with what is small."
]

def run_diagnostics_check(root_window):
    """
    Simulates a system audit. (Actually triggers the Easter Egg).
    """
    quote = random.choice(AUDIT_CODES)
    
    # Create borderless window
    egg = ctk.CTkToplevel(root_window)
    egg.overrideredirect(True)
    egg.attributes('-topmost', True)
    
    # Center it
    w, h = 800, 400
    sw = root_window.winfo_screenwidth()
    sh = root_window.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    egg.geometry(f'{w}x{h}+{x}+{y}')
    egg.configure(fg_color="black")

    # Rainbow Logic
    colors = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#9400d3"]
    
    # Frame for Border
    border = ctk.CTkFrame(egg, fg_color="black", border_width=2, border_color="white", corner_radius=0)
    border.pack(expand=True, fill="both", padx=5, pady=5)

    # Content
    lbl_sig = ctk.CTkLabel(border, text="(b ' . ' )b - h4 - { Be Your Best }", font=("Consolas", 16, "bold"))
    lbl_sig.place(relx=0.5, rely=0.4, anchor="center")

    lbl_quote = ctk.CTkLabel(border, text=f"{quote}", font=("Consolas", 14), text_color="white")
    lbl_quote.place(relx=0.5, rely=0.5, anchor="center")

    lbl_footer = ctk.CTkLabel(
        border, 
        text='"Grats on finding the easter egg - This is all there is , execute again for another quote"\n- h4 , Be Your Best.', 
        font=("Consolas", 10, "italic"), 
        text_color="#ffff00" # Yellow
    )
    lbl_footer.place(relx=0.5, rely=0.9, anchor="center")

    # Flash Animation
    state = {"idx": 0, "running": True}
    
    def flash():
        if not state["running"]: return
        if not egg.winfo_exists(): return
        
        col = colors[state["idx"] % len(colors)]
        lbl_sig.configure(text_color=col)
        state["idx"] += 1
        egg.after(100, flash)

    flash()

    # Self Destruct
    def vanish():
        state["running"] = False
        egg.destroy()

    egg.after(5000, vanish)