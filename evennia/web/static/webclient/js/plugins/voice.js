/*
 *
 * Evennia Webclient Voice IO plugin
 *
 */
let voicePlugin = (function () {

    var voice_enabled = false;
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition;
    var recognizing = false;

    //
    // Mandatory plugin init function
    var init = function () {
        // listener for the voice toggle
        $("#voice-toggle").on("change", function() {
            voice_enabled = this.checked;
            if (voice_enabled) {
                // Announce that voice is enabled.
                var utter = new SpeechSynthesisUtterance("Voice enabled.");
                speechSynthesis.speak(utter);
            }
        });

        // Speech-to-text setup
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';

            recognition.onstart = function() {
                recognizing = true;
                $("#mic-button").css('color', 'red');
            };

            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                Evennia.msg("text", [transcript], {});
            };

            recognition.onerror = function(event) {
                console.error("Speech recognition error", event.error);
            };

            recognition.onend = function() {
                recognizing = false;
                $("#mic-button").css('color', '');
            };

            $("#mic-button").on("click", function() {
                if (recognizing) {
                    recognition.stop();
                    return;
                }
                recognition.start();
            });

        } else {
            $("#mic-button").hide();
            console.log("Speech recognition not supported in this browser.");
        }

        console.log('Voice plugin initialized');
    }

    //
    // Text-to-speech handler
    var onText = function(args, kwargs) {
        if (voice_enabled) {
            var text = args[0];
            // The text from the server contains HTML. We need to strip it.
            var temp_div = document.createElement("div");
            temp_div.innerHTML = text;
            var stripped_text = temp_div.textContent || temp_div.innerText || "";

            if (stripped_text) {
                var utter = new SpeechSynthesisUtterance(stripped_text);
                speechSynthesis.speak(utter);
            }
        }
        return false; // let other plugins handle this too
    }

    return {
        init: init,
        onText: onText,
    }
})();
window.plugin_handler.add("voice", voicePlugin);
