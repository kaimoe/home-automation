//RGB settings
#define REFRESH_RATE 30
#define TRANSITION_DURATION 1
#define FADE_DURATION 5


struct RGB {
  float r;
  float g;
  float b;
};

RGB color;
RGB output;
float bright = 1.0;


const String color_names[16] = {
	"white",
	"silver",
	"gray",
	"black",
	"red",
	"maroon",
	"yellow",
	"olive",
	"lime",
	"green",
	"aqua",
	"teal",
	"blue",
	"navy",
	"fuchsia",
	"purple"
};

const int color_codes[16] = {
	0xffffff,
	0xc0c0c0,
	0x808080,
	0x000000,
	0xff0000,
	0x800000,
	0xffff00,
	0x808000,
	0x00ff00,
	0x008000,
	0x00ffff,
	0x008080,
	0x0000ff,
	0x000080,
	0xff00ff,
	0x800080
};

bool rgbIsLit() {
	if ((output.r + output.g + output.b) == 0) {
		return false;
	}
	return true;
}

void applyBright(RGB &rgb) {
	if (bright != 1.0) {
		rgb.r = rgb.r * bright;
		rgb.g = rgb.g * bright;
		rgb.b = rgb.b * bright;
	}
}

void setColor(RGB rgb) {
	Serial.print("Outputting ");
	Serial.print(rgb.r);
	Serial.print(" ");
	Serial.print(rgb.g);
	Serial.print(" ");
	Serial.println(rgb.b);
	output = rgb;
  analogWrite(RED_PIN, rgb.r);
  analogWrite(GREEN_PIN, rgb.g);
  analogWrite(BLUE_PIN, rgb.b);
}

float fetchBrightness(String &s) {
	if (s == "bright" || s == "full") {
		return 1.0;
	}
	if (s == "half") {
		return 0.5;
	}
	if (s == "dim" || s == "low") {
		return 0.25;
	}

	return -1.0;
}

int fetchColorCode(String &s) {
	int n = 16;
	int i = 0;
  while (i < n) {
    if (color_names[i] == s) {
      break;
    }
    i++;
  }

  if (i < n) {
		Serial.print("Fetched index ");
		Serial.println(i);
    return color_codes[i];
  }

	return -1;//NOTE: careful...
}

RGB hexToRGB(int h) {
  RGB rgb;
  rgb.r = h >> 16;
  rgb.g = (h >> 8) & 0xff;
  rgb.b = h & 0xff;
	Serial.print("Converted RGB ");
	Serial.print(rgb.r);
	Serial.print(" ");
	Serial.print(rgb.g);
	Serial.print(" ");
	Serial.println(rgb.b);
  return rgb;
}

void chgTrans(RGB new_color) {
	int N = REFRESH_RATE * TRANSITION_DURATION;

	RGB step;
	step.r = (new_color.r - output.r) / float(N);
	step.g = (new_color.g - output.g) / float(N);
	step.b = (new_color.b - output.b) / float(N);

	RGB step_color;
	for (int i = 0; i < N; i++) {
		step_color.r = output.r + step.r;
		step_color.g = output.g + step.g;
		step_color.b = output.b + step.b;
		setColor(step_color);
		delay((1/float(REFRESH_RATE))*1000);
	}
	setColor(new_color);
}

enum LightChanges {Instant, Transition, Pulse};

void changeLights(LightChanges change, RGB rgb) {
	color = rgb;
	applyBright(rgb);
	switch(change) {
		case Instant:
			setColor(rgb);
			break;
		case Transition:
			chgTrans(rgb);
			break;
	}
}

void handlePayload(String payload) {
	payload.toLowerCase();
	LightChanges change_type = Transition;
	//handle brightness
	float b = fetchBrightness(payload);
	if (b != -1.0) {
		Serial.print("Setting bright ");
		Serial.println(b);
		bright = b;
		changeLights(change_type, color);
		return;
	}


	//handle toggle/on/off
	if (payload == "toggle") {
		Serial.println("Toggling");
		if (rgbIsLit()) {
			chgTrans(hexToRGB(0));
		} else {
			changeLights(change_type, color);
		}
		return;
	}
	if (payload == "off") {
		Serial.println("Switch off");
		chgTrans(hexToRGB(0));
	}
	if (payload == "on") {
		Serial.println("Switch on");
		changeLights(change_type, color);
	}


	/*//handle pulse
	int code;
	if (payload.indexOf("pulse") != -1) {
		payload = payload.replace("pulse", "").replace(" ", "");
		if (payload == "") {
			code = 0;
		}
		change_type = Pulse;
	}*/

	//handle color
	int code = fetchColorCode(payload);
	if (code == -1) {
		Serial.print("Payload not recognized: ");
		Serial.println(payload);
		return;
	}
	changeLights(change_type, hexToRGB(code));
}

void autoDimming() {
	if (++dim_counter < dim_counter_max) return;
	else dim_counter = 0;

	//time-based dimming
	int day = rtc.getDay();
	int hour = rtc.getHours() + GMT;
	if ((last_dimmed_day != day) && (DIM_START_HOUR <= hour < DIM_END_HOUR) && (bright != 0.25)) {
		Serial.println("Auto-dimming");
		last_dimmed_day = day;
		bright = 0.25;
	} else if ((last_undimmed_day != day) && (hour < DIM_START_HOUR || hour >= DIM_END_HOUR) && (bright != 1.0)) {
		Serial.println("Auto-undimming");
		last_undimmed_day = day;
		bright = 1.0;
	} else return;
	if (rgbIsLit()) {
		changeLights(Transition, color);
	}
}
