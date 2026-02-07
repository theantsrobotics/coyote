// Basic PID controller

package org.firstinspires.ftc.teamcode;

import com.qualcomm.robotcore.util.ElapsedTime;


public class PIDController {
    private double kp;
    private double ki;
    private double kd;
    private boolean clegg;

    private double p;
    private double i;
    private double d;
    private boolean negative;
    private ElapsedTime timer;
    private double lastError;
    
    public PIDController(double kp, double ki, double kd, boolean clegg) {
        this.p = 0;
        this.i = 0;
        this.d = 0;
        this.kp = kp;
        this.ki = ki;
        this.kd = kd;
        this.clegg = clegg;
        this.timer = new ElapsedTime();
        this.reset();
    }

    public PIDController(double kp, double ki, double kd) {
        this(kp, ki, kd, false);
    }

    public void update(double error) {
        if (this.clegg && this.negative != (error > 0)) { // Clegg Integration
            this.negative = error > 0;
            this.i = 0;
        }
        double time = this.timer.time();
        this.p = error;
        this.i += error * time;
        this.d = (error - this.lastError) / time;
        this.lastError = error;
        this.timer.reset();
    }
    public void reset() {
        this.p = 0;
        this.i = 0;
        this.d = 0;
        this.lastError = 0;
        this.negative = false;
        this.timer.reset();
    }

    public double getSum() {
        return this.p * this.kp + this.i * this.ki + this.d * this.kd;
    }
}

