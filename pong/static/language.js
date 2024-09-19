document.addEventListener('DOMContentLoaded', () => {
    const translations = {
        fr: {
            labelWelcome: "BIENVENUE DANS LE PONG 42",
            labelNickname: "Entrez votre surnom:",
            labelPassword: "Entrez votre mot de passe:",
            labelConfirmPassword: "Confirmez votre mot de passe:",
            labelLoginPassword: "Entrez votre mot de passe:",
            labelSettings: "Paramètres",
            labelCheckNickname: "Vérifiez votre surnom:",
            labelLogin: "Se connecter",
            labelLocalGame: "Jeu local",
            labelQuickMatch: "Match rapide",
            labelTournament: "Tournoi",
            labelHome: "Accueil",
            labelRetry: "Rejouer"
        },
        en: {
            labelWelcome: "WELCOME TO PONG 42",
            labelNickname: "Enter your nickname:",
            labelPassword: "Enter your password:",
            labelConfirmPassword: "Confirm your password:",
            labelLoginPassword: "Enter your password:",
            labelSettings: "Settings",
            labelCheckNickname: "Check your nickname:",
            labelLogin: "Log in",
            labelLocalGame: "Local game",
            labelQuickMatch: "Quick match",
            labelTournament: "Tournament",
            labelHome: "Home",
            labelRetry: "Retry"
        },
        it: {
            labelWelcome: "BENVENUTO A PONG 42",
            labelNickname: "Inserisci il tuo soprannome:",
            labelPassword: "Inserisci la tua password:",
            labelConfirmPassword: "Conferma la tua password:",
            labelLoginPassword: "Inserisci la tua password:",
            labelSettings: "Impostazioni",
            labelCheckNickname: "Controlla il tuo soprannome:",
            labelLogin: "Accedi",
            labelLocalGame: "Gioco locale",
            labelQuickMatch: "Partita rapida",
            labelTournament: "Torneo",
            labelHome: "Home",
            labelRetry: "Riprova"
        },
        es: {
            labelWelcome: "BIENVENIDO A PONG 42",
            labelNickname: "Introduce tu apodo:",
            labelPassword: "Introduce tu contraseña:",
            labelConfirmPassword: "Confirma tu contraseña:",
            labelLoginPassword: "Introduce tu contraseña:",
            labelSettings: "Ajustes",
            labelCheckNickname: "Comprueba tu apodo:",
            labelLogin: "Iniciar sesión",
            labelLocalGame: "Juego local",
            labelQuickMatch: "Partida rápida",
            labelTournament: "Torneo",
            labelHome: "Inicio",
            labelRetry: "Reintentar"
        },
        de: {
            labelWelcome: "WILLKOMMEN BEI PONG 42",
            labelNickname: "Geben Sie Ihren Spitznamen ein:",
            labelPassword: "Geben Sie Ihr Passwort ein:",
            labelConfirmPassword: "Bestätigen Sie Ihr Passwort:",
            labelLoginPassword: "Geben Sie Ihr Passwort ein:",
            labelSettings: "Einstellungen",
            labelCheckNickname: "Überprüfen Sie Ihren Spitznamen:",
            labelLogin: "Anmelden",
            labelLocalGame: "Lokales Spiel",
            labelQuickMatch: "Schnelles Spiel",
            labelTournament: "Turnier",
            labelHome: "Startseite",
            labelRetry: "Wiederholen"
        },
        test: {
            labelWelcome: "1",
            labelNickname: "2",
            labelPassword: "3",
            labelConfirmPassword: "4",
            labelLoginPassword: "5",
            labelSettings: "6",
            labelCheckNickname: "7",
            labelLogin: "8",
            labelLocalGame: "9",
            labelQuickMatch: "10",
            labelTournament: "11",
            labelHome: "12",
            labelRetry: "13"
        }
    };

    function setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + (days*24*60*60*1000));
        const expires = "expires=" + d.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    function getCookie(name) {
        const cname = name + "=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(cname) === 0) {
                return c.substring(cname.length, c.length);
            }
        }
        return "";
    }

    function changeLanguage(lang) {
        setCookie('preferredLanguage', lang, 365);
        document.getElementById('welcome').innerText = translations[lang].labelWelcome;
        document.getElementById('label-nickname').innerText = translations[lang].labelNickname;
        document.getElementById('label-password').innerText = translations[lang].labelPassword;
        document.getElementById('label-confirm-password').innerText = translations[lang].labelConfirmPassword;
        document.getElementById('label-login-password').innerText = translations[lang].labelLoginPassword;
        document.getElementById('settings-btn').innerText = translations[lang].labelSettings;
        document.getElementById('check-nickname').innerText = translations[lang].labelCheckNickname;
        document.getElementById('login').innerText = translations[lang].labelLogin;
        document.getElementById('local-game').innerText = translations[lang].labelLocalGame;
        document.getElementById('quick-match').innerText = translations[lang].labelQuickMatch;
        document.getElementById('tournament').innerText = translations[lang].labelTournament;
        document.getElementById('home').innerText = translations[lang].labelHome;
        document.getElementById('retry').innerText = translations[lang].labelRetry;
    }

    function setLanguageFromCookie() {
        const preferredLanguage = getCookie('preferredLanguage');
        if (preferredLanguage && translations[preferredLanguage]) {
            changeLanguage(preferredLanguage);
        } else {
            changeLanguage('fr'); // Default to French if no cookie is found
        }
    }

    document.getElementById('lang-fr').addEventListener('click', () => changeLanguage('fr'));
    document.getElementById('lang-en').addEventListener('click', () => changeLanguage('en'));
    document.getElementById('lang-it').addEventListener('click', () => changeLanguage('it'));
    document.getElementById('lang-es').addEventListener('click', () => changeLanguage('es'));
    document.getElementById('lang-de').addEventListener('click', () => changeLanguage('de'));

    window.onload = setLanguageFromCookie;

    document.getElementById('settings-btn').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'block';
    });

    document.getElementById('close-settings').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'none';
    });

    
    document.getElementById('color-picker').addEventListener('input', function() {
        document.body.style.color = this.value;
        document.querySelectorAll('button').forEach(function(button) {
            button.style.backgroundColor = this.value;
        }, this);
    });

    document.getElementById('font-selector').addEventListener('change', function() {
        document.body.style.fontFamily = this.value;
    });

    document.getElementById('font-size-slider').addEventListener('input', function() {
        document.body.style.fontSize = this.value + 'px';
    });

});