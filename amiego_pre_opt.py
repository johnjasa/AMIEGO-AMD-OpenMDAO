"""
Inherits from Amiego driver to assign the pre continuous optimization hook.
"""
from six.moves import range

from openmdao.drivers.amiego_driver import AMIEGO_driver


class AMIEGO_With_Pre(AMIEGO_driver):

    def pre_cont_opt_hook(self):
        """
        Code goes here.
        """
        alloc_data = self.allocation_data
        num_route = alloc_data['num']
        num_existing_aircraft = alloc_data['num_existing']
        num_new_aircraft = alloc_data['num_new']
        num_aircraft = num_existing_aircraft + num_new_aircraft
        demand = alloc_data['demand']
        price = alloc_data['price_pax', 'CRM']
        route = alloc_data['range_km']

        x1_path = 'allocation_mission_group.revenue_comp.x1'
        x2_path = 'allocation_mission_group.revenue_comp.x2'
        y1_path = 'allocation_mission_group.revenue_comp.y1'
        y2_path = 'allocation_mission_group.revenue_comp.y2'
        z1_path = 'allocation_mission_group.revenue_comp.z1'

        trip = self.get_design_var_values()['allocation_mission_group.revenue_comp.flt_day'].T

        seats = []
        for key in allocation_data['names']:
            seats.append(alloc_data['capacity', key])
        seats = np.array(seats)

        #Include the bounds of the continuous variables
        #NOTE: alpha and beta are estimated without considering the max_avail_seats inside the Initialize class
        #NOTE: Matlab version calculates alpha and beta considering the max_avail_seats. Shouldn't be a problem though!
        x1 = np.ones((num_route, ))
        y1 = np.ones((num_route, ))
        x2 = np.ones((num_route, ))
        y2 = np.ones((num_route, ))
        z1 = np.zeros((num_route, ))
        for jj in range(num_route):
            av_seat = 0
            for kk in range(num_aircraft):
                x_kj = trip[jj, kk]
                av_seat += seats[kk]*x_kj

            if av_seat > 0:
                z1[jj] = av_seat
                alp, bet = demand_bounds(demand[jj], price[jj], route[jj])
                y1[jj] = np.floor(alp[0, 0]/bet[0, 0])
                y2[jj] = np.floor(alp[0, 1]/bet[0, 1])
                x1[jj] = np.floor(1.5*alp[0, 0]/bet[0, 0])
                x2[jj] = np.floor(1.5*alp[0, 1]/bet[0, 1])

        self.cont_opt._designvars[x1_path]['lower'] = x1
        self.cont_opt._designvars[x2_path]['lower'] = x2
        self.cont_opt._designvars[y1_path]['lower'] = y1
        self.cont_opt._designvars[y2_path]['lower'] = y2
        self.cont_opt._designvars[z1_path]['lower'] = z1
