#define stepPin 9
#define dirPin 8

  int pauseSteps = 400;

  int steps_per_revolution = 200;
  int gearing = 51;
  int rps = 60;
  int ustep = 400;
  int step_size = 5050/9;   // 5050 correlates to about 90 degrees
  int conversion_constant = 1;
  bool inverted = false;

  const byte numChars = 32;
  char receivedChars[numChars];   // an array to store the received data
  char tempChars[numChars];        // temporary array for use when parsing
  boolean newData = false;
  int data = 0;
  
  int LED_PIN = 13;
  
void setup() { 
  Serial.begin(115200); 
  Serial.println("Starting stepper"); 

  pinMode(stepPin, OUTPUT); 
  pinMode(dirPin, OUTPUT); 

  digitalWrite(dirPin, HIGH); 
  digitalWrite(stepPin, LOW); 

  pinMode(LED_PIN, OUTPUT);
  blipLED();
  
  print_help();
} 

void loop() { 
    rx_serial_data();

    if(newData) {
        strcpy(tempChars, receivedChars);
        parseData();
      
        if(receivedChars[0]==0x3F) {        // '?'    help
            print_help();
        }
        else if(receivedChars[0]==0x77) {   // 'w'    go up
            Serial.print("Moving up ");
            Serial.print(step_size);
            Serial.println(" microns");
            motor(HIGH,step_size);
        }
        else if(receivedChars[0]==0x73) {   // 's'    go down
            Serial.print("Moving down ");
            Serial.print(step_size);
            Serial.println(" microns");
            motor(LOW,step_size);
        }
        else if(receivedChars[0]==0x75) {   // 'u'    microstepping
            ustep = data;
            Serial.print("Setting microsteps to ");
            Serial.println(ustep);
            Serial.println("[Default = 400]");
        }
        else if(receivedChars[0]==0x76) {   // 'v'    velocity (rps)
            rps = data;
            Serial.print("Setting rotational velocity to ");
            Serial.print(rps);
            Serial.println("rps");
            Serial.println("[Default = 60]");
        }
        else if(receivedChars[0]==0x7A) {   // 'z'    steps to take
            step_size = data;
            Serial.print("Setting (count) step size to ");
            Serial.println(step_size);
            Serial.println("[Default = 1000]");
        }
        else if(receivedChars[0]==0x78) {   // 'x'    microns to take
            step_size = data*conversion_constant;
            Serial.print("Setting (step) step size to ");
            Serial.print(step_size);
            Serial.print(" (microns: ");
            Serial.print(step_size/conversion_constant);
            Serial.println(")");
            Serial.println("[Default = 1]");
        }
        else if(receivedChars[0]==0x63) {   // 'c'    conversion input
            conversion_constant = data;
            Serial.print("Setting conversion (um * c = steps) constant to ");
            Serial.println(conversion_constant);
            Serial.println("[Default = 1]");
        }
        else if(receivedChars[0]==0x70) {   // 'p'    pause steps
            pauseSteps = data;
            Serial.print("Setting pause size to ");
            Serial.println(pauseSteps);
            Serial.println("[Default = 400]");
        }
        else if(receivedChars[0]==0x69) {   // 'i'    invert direction
            if(data==1) {
                Serial.println("Direction is now inverted");
                inverted=true;
            }
            else if(data==0) {
                Serial.println("Direction is now non-inverted");
                inverted=false;
            }
            else {
                Serial.println("Invalid inverted state. Option are 0(non-inverted) or 1(inverted). Try again...");
            }
            
        }
        else if(receivedChars[0]==0x6C) {   // 'l'    blip LED
            blipLED();
            Serial.println("python says hi :)");
        }
        else {
            Serial.println("Invalid command. Type '?' for help...");
        }

        newData = false;
    }


      delay(200); 
            
}


void motor(bool DIR, long nSTP) {
  if(inverted) {
      digitalWrite(dirPin,!DIR); // Set direction 
  }
  else {
      digitalWrite(dirPin,DIR); // Set direction 
  }
  for(long x = 0; x < nSTP; x++) {         // Makes X pulses for making rotation 
        digitalWrite(stepPin,HIGH); 
        delayMicroseconds(pauseSteps); 
        digitalWrite(stepPin,LOW); 
        delayMicroseconds(pauseSteps); 
  } 
}

int degree_to_step(int d) {
    int uspr = steps_per_revolution * ustep * gearing;
    return d * uspr/360;
}

void rx_serial_data() {
    static byte ndx = 0;
    char endMarker = '\n';
    char rc;
    
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0'; // terminate the string
            ndx = 0;
            newData = true;
        }
    }
}

void parseData() {      // split the data into its parts
    char * strtokIndx;  // this is used by strtok() as an index

    strtokIndx = strtok(tempChars," ");       // get the first part - the string
    strtokIndx = strtok(NULL, "/n");           // this continues where the previous call left off
    data = atoi(strtokIndx);         // convert this part to an integer
}

void print_help() {
            Serial.println("-------------------HELP-MENU--------------------");
            Serial.println("Letter     Meaning              Expected Value                     Example  ");
            Serial.println("   ?       Help menu                                               ?");
            Serial.println("   u       Microstepping        Integer microsteps                 u 400");
            Serial.println("   v       Velocity             Rotational Speed (rps)             v 60");
            Serial.println("   z       Step Size            Steps to take (steps)              z 4000");
            Serial.println("   x       Step Size            Steps to take (microns)            x 10");
            Serial.println("   c       Conversion           um * c = steps                     c 971");
            Serial.println("   w       Go up                Go UP                              w");
            Serial.println("   s       Go down              Go DOWN                            s");
            Serial.println("   p       [ADV] Pause Steps    Adjust pause steps (advanced)      p 400");
            Serial.println("   i       Invert Direction     1 = inverted; 0 = noninverted      i 0");
            Serial.println("------------------/HELP-MENU--------------------");
}

void blipLED() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
}
