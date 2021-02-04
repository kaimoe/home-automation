//RGB settings
const int REFRESH_RATE = 30;
const int TRANSITION_DURATION = 2;
const int FADE_DURATION = 5;


struct RGB {
  float r;
  float g;
  float b;
};

RGB color;
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

int roundToInt(float f) {
	return (int) f + 0.5;
}

RGB applyBright(RGB &rgb) {
	if (bright != 1.0) {
		rgb.r = rgb.r * bright;
		rgb.g = rgb.g * bright;
		rgb.b = rgb.b * bright;
	}
}

void outputColor(RGB &rgb) {
	Serial.print("Outputting ");
	Serial.print(rgb.r);
	Serial.print(" ");
	Serial.print(rgb.g);
	Serial.print(" ");
	Serial.println(rgb.b);
  analogWrite(RED_PIN, rgb.r);
  analogWrite(GREEN_PIN, rgb.g);
  analogWrite(BLUE_PIN, rgb.b);
}

void setColor(RGB rgb) {
	color = rgb;
	applyBright(rgb);
	outputColor(rgb);
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
	step.r = (new_color.r - color.r) / float(N);
	step.g = (new_color.g - color.g) / float(N);
	step.b = (new_color.b - color.b) / float(N);

	RGB step_color;
	for (int i = 0; i < N; i++) {
		step_color.r = color.r + step.r;
		step_color.g = color.g + step.g;
		step_color.b = color.b + step.b;
		setColor(step_color);
		delay((1/float(REFRESH_RATE))*1000);
	}
	setColor(new_color);
}

void handlePayload(String payload) {
	int code = fetchColorCode(payload);
	if (code == -1) {
		Serial.print("Payload not recognized: ");
		Serial.println(payload);
		return;
	}
	chgTrans(hexToRGB(code));
}
