#include "Walbi.h"

namespace walbi_ns
{

Message read_message() { return (Message) Serial.read(); }

void write_message(enum Message myMessage)
{
    uint8_t* Message = (uint8_t*) &myMessage;
    Serial.write(Message, sizeof(uint8_t));
}

State lastState_;
unsigned long timestampLastHandledMessage_ = 0;

void Walbi::receivePositionFromDebugBoard_(uint8_t id, uint8_t command, uint16_t param1, uint16_t param2)
{
    (void)command;
    (void)param2;
    lastState_.positions[id] = param1;
    lastState_.is_position_updated[id] = true;
    //Check for incoherences in motor readings.
	if (param1 <= 10 || 1030 < param1) {
        lastState_.correct_motor_reading = false;
    }
    // TODO find index of array according to id, now we suppose the index and id are the same
}

void waitForSerial() // blocking until Serial available
{
    while (!Serial.available());
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
        action->commands[i][0] = read_i16(); // position
        action->commands[i][1] = read_i16(); // span
        action->commands[i][2] = read_i16(); // activate
    }
    write_message(OK);
    return true;
}

void Walbi::act(Action* action)
{
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        if (action->commands[i][2] > 0){
            this->servoBus_->MoveTime(this->motorIds[i], action->commands[i][0], action->commands[i][1]);
        } else {
            this->servoBus_->SetUnload(this->motorIds[i]);
        }
    }
}

State* Walbi::getState()
{
    lastState_.timestamp = millis();
    lastState_.correct_motor_reading = true;
    this->readPositionsFromDebugBoard_(); // will update correct_motor_reading if necessary
    lastState_.weight_left = this->weight_sensor_left_.read();
    lastState_.weight_right = this->weight_sensor_right_.read();

    return &lastState_;
}

bool Walbi::sendState(State* state)
{
    write_message(STATE);
    write_i32(state->timestamp);
    for (uint8_t i = 0; i < MOTOR_NB; i++)
    {
        write_i16(state->positions[i]);
        write_i8(state->is_position_updated[i]);
    }
    write_i32(state->weight_left);
    write_i32(state->weight_right);
    return waitAcknowledge();
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
            case RESET:
            {
                write_message(OK);
                State* statePtr = this->refreshStateIfNeeded_();
                return this->sendState(statePtr);
            }
            case STEP:
            {
                Action action;
                if (this->receiveAction(&action))
                {
                    this->act(&action);
                    State* statePtr = this->refreshStateIfNeeded_();
                    return this->sendState(statePtr);
                }
                else
                {
                    return false; // receiving action has failed
                }
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
            case VERSION:
            {
                int8_t version = read_i8();
                write_message(OK);
                write_message(VERSION);
                write_i8(PROTOCOL_VERSION);
                return waitAcknowledge();
            }
            case INFO:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_YET);
                return false;
            }
            case CLOSE:
            {
                write_message(ERROR);
                write_i8(NOT_IMPLEMENTED_YET);
                return false;
            }
            case OK:
            {
                write_message(ERROR);
                write_i8(DID_NOT_EXPECT_OK);
                return false;
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

State* Walbi::refreshStateIfNeeded_() {
    if (millis() - lastState_.timestamp >= this->intervalRefreshState_)
    {
		return this->getState();
	}
    return &lastState_;
}

void Walbi::run()
{
	if (millis() - timestampLastHandledMessage_ >= this->intervalReadSerial_)
    {
		timestampLastHandledMessage_ = millis();
		this->handleMessagesFromSerial();
	}
	this->refreshStateIfNeeded_();
}

Walbi::Walbi(Stream* debugBoardStream, unsigned long intervalReadSerial, unsigned long intervalRefreshState):
    intervalReadSerial_(intervalReadSerial), intervalRefreshState_(intervalRefreshState)
{
    this->servoBus_ = new ServoBus(debugBoardStream, 13);
    this->servoBus_->setEventHandler(REPLY_POSITION, this->receivePositionFromDebugBoard_);
    memcpy(this->motorIds, MOTOR_IDS, sizeof(this->motorIds)); // init ids with MOTOR_IDS
}

Walbi::begin(long computerSerialBaud, unsigned char dout_left, unsigned char dout_right, unsigned char pd_sck_left, unsigned char pd_sck_right, bool autoConnect, unsigned long delay_ready)
{
    Serial.begin(computerSerialBaud);

    this->weight_sensor_left_.begin(dout_left, pd_sck_left);
	this->weight_sensor_right_.begin(dout_right, pd_sck_right);
    delay(delay_ready);

    if (autoConnect) { this->connect(); }
}

} // namespace walbi_ns
