#include "Walbi.h"

namespace walbi_ns
{

State lastState_;
unsigned long timestampLastHandledMessage_ = 0;
unsigned long timestampLastSendState_ = 0;

// unique constructor
Walbi::Walbi(Stream* debugBoardStream, uint8_t imu_address, unsigned long intervalReadSerial, unsigned long intervalRefreshState):
    imu(imu_address), intervalReadSerial_(intervalReadSerial), intervalRefreshState_(intervalRefreshState)
{
    this->servoBus_ = new ServoBus(debugBoardStream, 13);
    this->servoBus_->setEventHandler(REPLY_POSITION, this->receivePositionFromDebugBoard_);
    memcpy(this->motorIds, MOTOR_IDS, sizeof(this->motorIds)); // init ids with MOTOR_IDS
}

void Walbi::begin(long computerSerialBaud, unsigned char dout_left, unsigned char dout_right, unsigned char pd_sck_left, unsigned char pd_sck_right, bool autoConnect, unsigned long delay_ready)
{
    Serial.begin(computerSerialBaud);
    int success = this->imu.begin(); // TODO react to failure

    this->weight_sensor_left_.begin(dout_left, pd_sck_left);
	this->weight_sensor_right_.begin(dout_right, pd_sck_right);
    delay(delay_ready);

    if (autoConnect) { this->connect(); }
}

void Walbi::receivePositionFromDebugBoard_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)command;
    (void)param2;
    lastState_.position[id] = param1;
    lastState_.is_position_updated[id] = true;
    // Check for incoherences in motor readings
	if (param1 <= 10 || 1030 < param1) {
        lastState_.correct_motor_reading = false;
    }
    // TODO find index of array according to id, now we suppose the index and id are the same
}

State* Walbi::readPositionsFromDebugBoard_()
{
    memset(lastState_.is_position_updated, 0, sizeof(bool) * MOTOR_NB);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        this->servoBus_->requestPosition(this->motorIds[i]);
    }
    return &lastState_;
}

State* Walbi::getState()
{
    lastState_.timestamp = millis();
    lastState_.correct_motor_reading = true;
    this->readPositionsFromDebugBoard_(); // will update correct_motor_reading if necessary
    lastState_.weight_left = this->weight_sensor_left_.read();
    lastState_.weight_right = this->weight_sensor_right_.read();
    lastState_.imu[0] = imu.convertAccel(imu.ax);
    lastState_.imu[1] = imu.convertAccel(imu.ay);
    lastState_.imu[2] = imu.convertAccel(imu.az);
    lastState_.imu[3] = imu.convertGyro(imu.gx);
    lastState_.imu[4] = imu.convertGyro(imu.gx);
    lastState_.imu[5] = imu.convertGyro(imu.gx);
    lastState_.imu[6] = imu.convertAngleDeg(imu.roll);
    lastState_.imu[7] = imu.convertAngleDeg(imu.pitch);
    lastState_.imu[8] = imu.convertAngleDeg(imu.yaw);
    return &lastState_;
}

void Walbi::act(Action* action)
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        if (action->activate[i]){
            this->servoBus_->MoveTime(this->motorIds[i], action->position[i], action->span[i]);
        } else {
            this->servoBus_->SetUnload(this->motorIds[i]);
        }
    }
}

State* Walbi::refreshStateIfNeeded_() {
    if (millis() - lastState_.timestamp >= this->intervalRefreshState_)
    {
		return this->getState();
	}
    return &lastState_;
}


// Communication methods

void waitForSerial() // blocking until Serial available
{
    while (!Serial.available());
}

Message read_message() { return (Message) Serial.read(); }

void write_message(enum Message myMessage)
{
    uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

bool waitAcknowledge()
{
    waitForSerial();
    Message messageReceived = read_message();
    if(messageReceived != OK)
    {
        write_message(ERROR);
        write_i8(EXPECTED_OK);
        return false;
    }
    return true;
}

bool Walbi::connect()
{
    while(!this->isConnected)
    {
        write_message(CONNECT);
        wait_for_bytes(1, 1000);
        this->handleMessagesFromSerial();
    }
    return this->isConnected;
}

bool Walbi::receiveAction(Action* action)
{
    // assume ACTION msg already received
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        action->position[i] = read_i16(); // position
        action->span[i] = read_i16(); // span
        action->activate[i] = bool(read_i8()); // activate
    }
    write_message(OK);
    return true;
}

bool Walbi::sendState(State* state)
{
    write_message(STATE);
    write_i32(state->timestamp);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(state->position[i]);
        write_i8(state->is_position_updated[i]);
    }
    write_i8(state->correct_motor_reading);
    write_i32(state->weight_left);
    write_i32(state->weight_right);
    for (uint8_t i = 0; i < 9; i++)
    {
        write_i16(state->imu[i]); // [ax, ay, az, gx, gy, gz, roll, pitch, yaw]
    }
    if waitAcknowledge()
    {
        timestampLastSendState_ = millis();
        return true;
    }
    return false;
}

bool Walbi::sendStateIfNeeded_(State* state)
{
    if (this->isConnected && millis() - timestampLastSendState_ >= this->intervalSendState_)
    {
		this->sendState(state);
	}
}

void Walbi::run()
{
	if (millis() - timestampLastHandledMessage_ >= this->intervalReadSerial_)
    {
		timestampLastHandledMessage_ = millis();
		this->handleMessagesFromSerial();
	}
	this->refreshStateIfNeeded_();
    this->sendStateIfNeeded_();
}

bool Walbi::handleMessagesFromSerial()
{
    if(Serial.available() > 0) // non blocking, do not use wait_for_serial
    {
        Message messageReceived = read_message(); // The first byte received is the instruction
        switch(messageReceived)
        {
            case CONNECT:
            {
                // If the we have not said hello, check the connection
                if(!this->isConnected)
                {
                    this->isConnected = true;
                    write_message(CONNECT);
                }
                else
                {
                    // If we are already connected do not send "connect" to avoid infinite loop
                    write_message(ALREADY_CONNECTED);
                }
                return true;
            }
            case ALREADY_CONNECTED: { this->isConnected = true; return true; }
            case ERROR:
            {
                write_message(ERROR);
                write_i8(DID_NOT_EXPECT_MESSAGE);  // We are sending the errors !
                return false;
            }
            case VERSION:
            {
                int8_t version = read_i8();
                write_message(OK);
                write_message(VERSION);
                write_i8(PROTOCOL_VERSION);
                return waitAcknowledge();
            }
            case SET:
            {
                this->intervalSendState_ = read_i32();
                write_message(OK);
                return true;
            }
            case ACTION:
            {
                // only happens if agent is controlling without reading state
                Action action;
                if (this->receiveAction(&action))
                {
                    this->act(&action);
                    return true;
                }
                else
                {
                    return false; // receiving action has failed
                }
            }
            case STATE:
            {
                write_message(OK);
                State* statePtr = this->refreshStateIfNeeded_();
                return this->sendState(statePtr);
            }
            // Unknown message
            default:
            {
                write_message(ERROR);
                write_i8(RECEIVED_UNKNOWN_MESSAGE);
                return false;
            }
        }
    }
    return true; // empty serial buffer is a successful message handling
}

} // namespace walbi_ns
