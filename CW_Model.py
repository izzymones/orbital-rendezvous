import numpy as np
import casadi as ca
import do_mpc

from constants import Constants
mc = Constants()


class CWModel:
    def __init__(self, mc):
        self.mc = mc

        self.model = do_mpc.model.Model('continuous' , 'SX')
        r = self.model.set_variable(var_type='_x', var_name='r', shape=(3,1))
        v = self.model.set_variable(var_type='_x', var_name='v', shape=(3,1))

        self.state = ca.vertcat(r,v)
        self.u = self.model.set_variable(var_type='_u', var_name='u', shape=(3,1))
        self.control = ca.vertcat(self.u)

        vx_dot = 2*self.mc.n*v[1] + 3*self.mc.n**2*r[0] + self.u[0]
        vy_dot = -2*self.mc.n*v[0] + self.u[1]
        vz_dot = -self.mc.n**2*r[2] + self.u[2]
        v_dot = ca.vertcat(vx_dot,vy_dot,vz_dot)
        
        self.model.set_rhs('r', v)
        self.model.set_rhs('v', v_dot)

        self.dynamics = ca.vertcat(
            v,
            v_dot
        )

        # build the cost function
        x_r = ca.DM(self.mc.xr).reshape((6,1))
        x_error = self.state - x_r
        x_cost = x_error.T @ self.mc.Q @ x_error 
        terminal_cost = x_error.T @ (self.mc.terminal_cost_factor * self.mc.Q) @ x_error 
        u_goal = ca.DM(self.mc.ur).reshape((3,1))
        u_error = self.u - u_goal
        u_cost = u_error.T @ self.mc.R @ u_error
        cost = x_cost + u_cost
        self.model.set_expression(expr_name='terminal_cost', expr=terminal_cost )
        self.model.set_expression(expr_name='cost', expr=cost)

        self.model.setup()