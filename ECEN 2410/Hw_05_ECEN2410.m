
% Load weather data from SAM (System Advisor Model) format CSV
weatherFile = 'TusconWeatherData.csv';
T = load_sam_weather(weatherFile);

% Load actual PV generation data calculated from Python script
% pvData = readmatrix('panel_string_power.csv');
% P_pv_actual = pvData(:,2);  % Extract power values (kW)

% Define PV system parameters for forecast calculations
pvParams = struct();
pvParams.phi = 38.89;          % Site latitude [deg]
pvParams.beta_deg = 25;        % Panel tilt angle [deg]
pvParams.kv = 1.5;             % Wind speed temperature coefficient [deg C per (m/s)]
pvParams.NOCT = 44.9;          % Nominal Operating Cell Temperature [deg C]
pvParams.P_mod_STC = 739.411;  % Module power at STC [W]
pvParams.Vmp_STC = 46.3;       % Maximum power point voltage at STC [V]
pvParams.Vmp_Tcoef = -0.121;   % Vmp temperature coefficient [V/deg C]
pvParams.gammaT = -0.00247;    % Power temperature coefficient [1/deg C]
pvParams.Ns = 4;               % Number of modules in series
pvParams.eta_inv = 0.9738;     % Inverter efficiency

% Define forecasting methods to evaluate
methods = {'persistence'};
numMethods = numel(methods);

% Generate forecast results for July
weeks = struct('name', 'July', 'days', 183:189);
forecastWeeks = struct();
for w = 1:numel(weeks)
    weekName = weeks(w).name;
    weekDays = weeks(w).days;
    forecastWeeks.(weekName).actual = cell(1, numel(weekDays));    % Store actual PV data
    forecastWeeks.(weekName).forecast = cell(1, numel(weekDays));  % Store forecast data
    for d = 1:numel(weekDays)
        dayNum = weekDays(d);
        idx_day = (dayNum-1)*24 + (1:24);        % Indices for current day (24 hours)
        idx_hist = idx_day(1) - 168 : idx_day(1) - 1;  % Indices for previous 7 days
%        actualDayP = P_pv_actual(idx_day);       % Actual PV power for the day
        forecastSeries = zeros(24, numMethods); % Initialize forecast array
        
        % Generate forecasts using each method
        for m = 1:numMethods
            method = methods{m};
            % Forecast weather parameters for the day
            [GHI_f, DNI_f, DHI_f, Tamb_f, alb_f, wind_f] = forecast_weather(T(idx_hist, :), method);
            % Compute PV power forecast
            forecastSeries(:,m) = compute_pv_from_forecast(GHI_f, DNI_f, DHI_f, Tamb_f, alb_f, wind_f, idx_day, pvParams);
        end
%        forecastWeeks.(weekName).actual{d} = actualDayP;
        forecastWeeks.(weekName).forecast{d} = forecastSeries;
    end
end

% Load hourly residential demand
Demand = readmatrix('tucson_residential_demand.csv');
if size(Demand,2) < 2
    error('tucson_residential_demand.csv must contain at least two columns: hour index and demand.');
end
P_demand = Demand(:,2);
if length(P_demand) ~= 8760
    warning('Demand CSV length (%d) does not match weather data length (%d).', length(P_demand), N);
end


% I have spent an embarrassing amount of time trying to optimize this code.
% The algorithm sorts the demand from high to low, lowers the demand at
% peaks as much as possible and distributes it across the lower demand
% values as much as possible. This is the reason that this assignment is
% getting turned in late :(
% It could be further optimized but I would rather turn in my
% spaghetti code than something made up by the water-wasting machines.
function [Demand_day_adj] = flexDemandTest(demand_day)
    
    max_flex = 0.2 * demand_day;
    avg_demand = mean(demand_day);
    
    flex_down = zeros(size(demand_day));
    flex_up   = zeros(size(demand_day));
    
    [sorted_demand, idx_demand] = sort(demand_day, 'descend');
    
    remaining_flex_down = sum(max_flex) / 2;
    for h = 1:24
        i = idx_demand(h);
        flex_down(i) = min([max_flex(i), max(sorted_demand(h) - avg_demand, 0), remaining_flex_down]);
        remaining_flex_down = remaining_flex_down - flex_down(i);
    end
    
    remaining_flex_up = sum(flex_down);
    for h = 24:-1:1
        i = idx_demand(h);
        flex_up(i) = min(max_flex(i), max([avg_demand - sorted_demand(h), 0, remaining_flex_up]));
        remaining_flex_up = remaining_flex_up - flex_up(i);
    end
    Demand_day_adj = demand_day - flex_down + flex_up;
    % disp(sum(demand_day) - sum(Demand_day_adj)); % uncomment this line
    % for a demonstration that the error is a floating point calculation
    % error and is negligible
end

function [scheduled_cost, P_grid_sched, P_ch, P_dis, E] = optimize_battery(P_fcst, P_demand, TOU_price, E_ini, is_offpeak, is_onpeak)
E_max = 13.5;
P_max = 4.5;
E_min = 0.20 * E_max;
E_target = 0.50 * E_max;
RTE = 0.95;
eta_c = sqrt(RTE);
eta_d = sqrt(RTE);

N = 24;
P_ch = zeros(N,1);
P_dis = zeros(N,1);
E = zeros(N,1);
P_grid_sched = zeros(N, 1);
scheduled_cost = zeros(N, 1);

E_prev = E_ini;
future_excess = max(0, P_fcst - P_demand);

    for t = 1:N
        E_prev = min(max(E_prev, E_min), E_max);
        forecast_excess = max(0, P_fcst(t) - P_demand(t));   
        forecast_deficit = max(0, P_demand(t) - P_fcst(t));
        planned_pv_charge = min([forecast_excess, P_max, (E_max - E_prev) / eta_c]);
        
        predicted_excess = 0;
        if t < N
            predicted_excess = sum(future_excess(t+1:end)); %remaining predicted excess energy for the day
        end
        energy_needed_to_target = max(0, (E_target - (E_prev + eta_c * planned_pv_charge)) / eta_c); % determines how much energy will be required to draw from grid in order to reach 50% charge
        
        planned_grid_charge = 0;
        if is_offpeak(t) && ((E_prev + eta_c * planned_pv_charge) < E_target) % if its offpeak and the planned energy production is less than what is needed to charge
            if predicted_excess < energy_needed_to_target
                planned_grid_charge = min([P_max - planned_pv_charge, energy_needed_to_target - predicted_excess, (E_max - (E_prev + eta_c * planned_pv_charge)) / eta_c]);
            end
        end
    
        charge_power = planned_pv_charge + planned_grid_charge;
        discharge_power = 0;
        if is_onpeak(t)
            max_discharge = min([P_max, (E_prev + eta_c * charge_power - E_min) * eta_d, forecast_deficit]);
            discharge_power = max(0, max_discharge);
        end
    
        P_ch(t) = charge_power;
        P_dis(t) = discharge_power;
    
        E_curr = E_prev + eta_c * P_ch(t) - P_dis(t) / eta_d;
        E_curr = min(max(E_curr, E_min), E_max);
        E(t) = E_curr;
    
        P_grid_sched(t) = max(0, P_demand(t) - P_fcst(t) + P_ch(t) - P_dis(t));
        scheduled_cost(t) = P_grid_sched(t) * TOU_price(t);
    
        E_prev = E_curr;
    end
end

julyWeek = 182:188;
bestMethodName = 'persistence';

schemes = {'three_tier_TOU'};
schemeLabels = {'Three-Tier TOU'};
numSchemes = numel(schemes);
scheduleResults = struct();


for s = 1:numSchemes
    schemeName = schemes{s};
    scheduleResults.(schemeName).P_grid_adj = zeros(168,1);
    scheduleResults.(schemeName).P_ch_adj = zeros(168,1);
    scheduleResults.(schemeName).P_dis_adj = zeros(168,1);
    scheduleResults.(schemeName).E_adj = zeros(168,1);
    scheduleResults.(schemeName).cost_hour_adj = zeros(168,1);
    scheduleResults.(schemeName).Demand_adj = zeros(168,1);

    scheduleResults.(schemeName).P_grid_sched = zeros(168,1);
    scheduleResults.(schemeName).P_ch_sched = zeros(168, 1);
    scheduleResults.(schemeName).P_dis_sched = zeros(168,1);
    scheduleResults.(schemeName).E_sched = zeros(168,1);
    scheduleResults.(schemeName).scheduled_cost = zeros(168,1);
    scheduleResults.(schemeName).Demand = zeros(168,1);
end

for day = julyWeek % yearlong battery scheduling loop
    idx_day = (day-1) * 24 + (1:24);
    idx_hist = idx_day(1) - 168 :idx_day(1);
    P_demand_day = P_demand(idx_day);
    P_pv_actual_day = P_pv_actual(idx_day);
    [GHI_f, DNI_f, DHI_f, Tamb_f, alb_f, wind_f] = forecast_weather(T(idx_hist, :), bestMethodName);
    P_pv_forecast_day = compute_pv_from_forecast(GHI_f, DNI_f, DHI_f, Tamb_f, alb_f, wind_f, idx_day, pvParams);

    for s = 1:numSchemes
        schemeName = schemes{s};  
        [TOU_price, is_offpeak, is_onpeak] = build_daily_price(day, schemeName);
        
        [Demand_day_adj] = flexDemandTest(P_demand_day);

        E_ini = 0.5 * 13.5;
        [P_grid_adj, P_ch_adj, P_dis_adj, E_adj, cost_hour_adj] = schedule_battery_day(P_pv_forecast_day, P_pv_actual_day, Demand_day_adj, TOU_price, is_offpeak, is_onpeak, E_ini); % uses adjusted demand
        [P_grid, P_ch, P_dis, E, cost_hour] = schedule_battery_day(P_pv_forecast_day, P_pv_actual_day, P_demand_day, TOU_price, is_offpeak, is_onpeak, E_ini); % uses base demand
        
        %storage of scheduling data
        scheduleResults.(schemeName).P_grid_adj(idx_day) = P_grid_adj;
        scheduleResults.(schemeName).P_ch_adj(idx_day) = P_ch_adj;
        scheduleResults.(schemeName).P_dis_adj(idx_day) = P_dis_adj;
        scheduleResults.(schemeName).E_adj(idx_day) = E_adj;
        scheduleResults.(schemeName).cost_hour_adj(idx_day) = cost_hour_adj;
        scheduleResults.(schemeName).Demand_adj(idx_day) = Demand_day_adj;

        scheduleResults.(schemeName).P_grid_sched(idx_day) = P_grid;
        scheduleResults.(schemeName).P_ch_sched(idx_day) = P_ch;
        scheduleResults.(schemeName).P_dis_sched(idx_day) = P_dis;
        scheduleResults.(schemeName).E_sched(idx_day) = E;
        scheduleResults.(schemeName).scheduled_cost(idx_day) = cost_hour;
        scheduleResults.(schemeName).Demand(idx_day) = P_demand_day;
    end
end

%below is all figures

julyHours = (julyWeek(1)-1)*24 + 1 : julyWeek(end)*24;

for s = 1:numSchemes
    scheme = schemes{s};
    % Charging/Discharging And Power Plots
    figure('Name', ['Battery Analysis: ' schemeLabels{s}], 'Color', 'w');

    subplot(2, 1, 1);
    hold on;
    b1 = bar(julyHours, scheduleResults.(scheme).P_ch_sched(julyHours), 'FaceColor', [0.2 0.6 1], 'EdgeColor', 'none', 'DisplayName', 'Charge');
    b2 = bar(julyHours, -scheduleResults.(scheme).P_dis_sched(julyHours), 'FaceColor', [1 0.4 0.4], 'EdgeColor', 'none', 'DisplayName', 'Discharge');
    
    title(['Battery Schedule: Baseline Demand (', schemeLabels{s}, ')']);
    ylabel('Power [kW]');
    ylim([-5 5]); grid on;
    legend([b1 b2], 'Location', 'northeast');

    subplot(2, 1, 2);
    hold on;
    bar(julyHours, scheduleResults.(scheme).P_ch_adj(julyHours), 'FaceColor', [0.2 0.6 1], 'EdgeColor', 'none');
    bar(julyHours, -scheduleResults.(scheme).P_dis_adj(julyHours), 'FaceColor', [1 0.4 0.4], 'EdgeColor', 'none');
    
    title(['Battery Schedule: Flexed Demand (', schemeLabels{s}, ')']);
    ylabel('Power [kW]');
    xlabel('Hour of the Year (July Week)');
    ylim([-5 5]); grid on;

    % Demand Plots
    figure('Name', ['Demand Analysis: ' schemeLabels{s}], 'Color', 'w');

    subplot(2, 1, 1);
    hold on;
    bar(julyHours, scheduleResults.(scheme).Demand(julyHours), 'FaceColor', [0.2 0.6 1]);

    title(['Battery Schedule: Baseline Demand (', schemeLabels{s}, ')']);
    ylabel('Demand [kW]');
    ylim([-5 5]); grid on;

    subplot(2, 1, 2);
    hold on;
    bar(julyHours, scheduleResults.(scheme).Demand_adj(julyHours), 'FaceColor', [1 0.6 .2]);

    title(['Battery Schedule: Flexed Demand (', schemeLabels{s}, ')']);
    ylabel('Demand [kW]');
    xlabel('Hour of the Year (July Week)');
    ylim([-5 5]); grid on;

    % SOC plot
    figure('Name', ['State Of Charge: ' schemeLabels{s}], 'Color', 'w');

    subplot(2, 1, 1);
    hold on;
    bar(julyHours, scheduleResults.(scheme).E_sched(julyHours), 'FaceColor', [0.2 0.6 1]);

    title(['Battery Schedule: Baseline Demand (', schemeLabels{s}, ')']);
    ylabel('Energy [kWh]');
    ylim([2.5 14]); grid on;

    subplot(2, 1, 2);
    hold on;
    bar(julyHours, scheduleResults.(scheme).E_adj(julyHours), 'FaceColor', [1 0.6 .2]);

    title(['Battery Schedule: Flexed Demand (', schemeLabels{s}, ')']);
    ylabel('Energy [kWh]');
    xlabel('Hour of the Year (July Week)');
    ylim([2.5 14]); grid on;

end
% Question 2:
disp("Adjusted Demand Total Cost [$]:");
disp(sum(scheduleResults.three_tier_TOU.cost_hour_adj));
disp("Fixed Demand Total Cost [$]:");
disp(sum(scheduleResults.three_tier_TOU.scheduled_cost));
disp('Cost Difference [$]:');
disp(sum(scheduleResults.three_tier_TOU.scheduled_cost) - sum(scheduleResults.three_tier_TOU.cost_hour_adj));

disp("The demand profile becomes more smooth when variable demand is introduced. This is because the demand can be reduced during peak" + newline + ...
    "hours, and compensated for during off-peak hours in order to reduce cost. The battery tends to charge and discharge less overall" + newline + ...
    "when demand is variable, as the demand is higher during periods where solar power is available. " + newline + newline + ...
    "The battery becomes less valuable when demand flexibility is introduced, because the role of the battery is to shift the power drawn" + newline + ...
    "over time so that the power consumed is overall cheaper. When demand is variable, this purpose is achieved to a certain degree as a " + newline + ...
    "result of demand shifting to when the power is cheaper/more avaialable. This is demonstrated by Figure 1: Battery Analysis, which shows" + newline + ...
    "a reduction in the magnitude of battery charging/discharging periods, and Figure 3: State Of Charge, which shows lower values that the" + newline + ...
    "battery charges by when solar is available. This is due to demand shifting towards when solar power is available, and away from when cost is high." + newline);
disp("Demand is shifted under TOU pricing because it is advantageous to consume less power during high-cost times and more power during low-cost" + newline + ...
    "times. This leads to demand being lowered when the TOU price is high, and being raised when the TOU price is low." + newline + newline + ...
    "Tou pricing creates incentives for both battery usage and demand shifting because it rewards consumption of power when the cost of energy is low." + newline + ...
    "Battery systems take advantage of this by charging when the TOU price is low and discharging when the TOU price is high, effectively reducing" + newline + ...
    "the amount of high-cost power that is consumed. Demand shifting takes advantage of this incentive by shifting the consumption of electricity itslef" + newline + ...
    "from times when it is more expensive to times when the cost is lower.");

%============================================================================
% Helper Functions
%============================================================================
function T = load_sam_weather(filename)
    data = readmatrix(filename);
    if size(data,2) < 15
        error('Expected at least 15 columns in %s.', filename);
    end

    T = table();
    T.Year    = data(:,1);
    T.Month   = data(:,2);
    T.Day     = data(:,3);
    T.Hour    = data(:,4);
    T.Minute  = data(:,5);
    T.DNI     = data(:,6);
    T.DHI     = data(:,7);
    T.GHI     = data(:,8);
    T.DewPoint= data(:,9);
    T.Tamb    = data(:,10);
    T.Pressure= data(:,11);
    T.RH      = data(:,12);
    T.windDir = data(:,13);
    T.wind    = data(:,14);
    T.albedo  = data(:,15);
    T.t_solar = T.Hour + T.Minute ./ 60;
end

function P_pv = compute_pv_from_forecast(GHI_f, DNI_f, DHI_f, Tamb_f, alb_f, wind_f, idx_day, params)
    hourOfDay = mod(idx_day - 1, 24);
    t_solar = hourOfDay + 0.5;
    targetDay = ceil(idx_day(1) / 24);
    doy = targetDay;

    delta = 23.45 .* sind((360/365) .* (284 + doy));
    omega = 15 .* (t_solar - 12);
    cos_tz = sind(params.phi) .* sind(delta) + cosd(params.phi) .* cosd(delta) .* cosd(omega);
    cos_tz = max(-1, min(1, cos_tz));
    daylight = cos_tz > 0;

    cos_ti = ...
        sind(delta).*sind(params.phi).*cosd(params.beta_deg) ...
      - sind(delta).*cosd(params.phi).*sind(params.beta_deg) ...
      + cosd(delta).*cosd(params.phi).*cosd(params.beta_deg).*cosd(omega) ...
      + cosd(delta).*sind(params.phi).*sind(params.beta_deg).*cosd(omega);

    GPOA = zeros(24,1);
    for k = 1:24
        if daylight(k)
            if cos_ti(k) > 0
                GPOA(k) = DNI_f(k) * cos_ti(k) + DHI_f(k) * (1 + cosd(params.beta_deg)) / 2 + ...
                          alb_f(k) * GHI_f(k) * (1 - cosd(params.beta_deg)) / 2;
            else
                GPOA(k) = DHI_f(k) * (1 + cosd(params.beta_deg)) / 2 + ...
                          alb_f(k) * GHI_f(k) * (1 - cosd(params.beta_deg)) / 2;
            end
        end
    end

    Tcell = Tamb_f + (((params.NOCT - 20) / 800) .* GPOA) - (params.kv .* wind_f);
    Tcell = max(Tcell, Tamb_f);
    P_mod = params.P_mod_STC .* (GPOA ./ 1000) .* (1 + params.gammaT .* (Tcell - 25));
    P_mod = max(P_mod, 0);
    P_pv = params.Ns .* P_mod .* params.eta_inv ./ 1000;
end

function [GHI_f, DNI_f, DHI_f, Tamb_f, albedo_f, wind_f] = forecast_weather(T_past7, method)
    variables = {'GHI', 'DNI', 'DHI', 'Tamb', 'albedo', 'wind'};
    results = cell(1, 6);

    for i = 1:6
        var_name = variables{i};
        data = T_past7.(var_name);
        if strcmp(method, 'persistence')
            results{i} = data(145:168);
        elseif strcmp(method, 'moving_avg')
            d1 = data(145:168);
            d2 = data(121:144);
            d3 = data(97:120);
            results{i} = (d1 + d2 + d3) / 3;
        elseif strcmp(method, 'linear')
            x_days = (1:7)';
            x_target = 8;
            data_fcst = zeros(24,1);
            for h = 1:24
                idx_h = h:24:168;
                p = polyfit(x_days, data(idx_h), 1);
                data_fcst(h) = polyval(p, x_target);
            end
            if ~strcmp(var_name, 'Tamb')
                data_fcst = max(0, data_fcst);
            end
            results{i} = data_fcst;
        else
            error('Method not valid. Use: persistence, moving_avg, or linear');
        end
    end

    GHI_f    = results{1};
    DNI_f    = results{2};
    DHI_f    = results{3};
    Tamb_f   = results{4};
    albedo_f = results{5};
    wind_f   = results{6};
end

function [TOU_price, is_offpeak, is_onpeak] = build_daily_price(dayNumber, schemeName)
    date = datetime(2024,1,1) + days(dayNumber-1);
    if month(date) >= 6 && month(date) <= 9
        season = 'summer';
    else
        season = 'winter';
    end

    h = (1:24)';
    switch schemeName
        case 'flat_rate'
            TOU_price = 0.14 * ones(24,1);
        case 'current_TOU'
            if strcmp(season, 'summer')
                TOU_price = [0.11*ones(17,1); 0.28*ones(4,1); 0.11*ones(3,1)];
            else
                TOU_price = [0.10*ones(17,1); 0.22*ones(4,1); 0.10*ones(3,1)];
            end
        case 'three_tier_TOU'
            if strcmp(season, 'summer')
                TOU_price = [0.10*ones(9,1); 0.15*ones(5,1); 0.25*ones(4,1); 0.15*ones(3,1); 0.10*ones(3,1)];
            else
                TOU_price = [0.09*ones(9,1); 0.13*ones(8,1); 0.20*ones(2,1); 0.13*ones(2,1); 0.09*ones(3,1)];
            end
        otherwise
            error('Unknown pricing scheme %s.', schemeName);
    end

    is_offpeak = TOU_price == min(TOU_price);
    is_onpeak = TOU_price == max(TOU_price);
end

function [P_grid, P_ch, P_dis, E, cost_hour] = schedule_battery_day(P_fcst, P_actual, P_demand, TOU_price, is_offpeak, is_onpeak, E_ini)
    E_max = 13.5;
    P_max = 4.5;
    E_min = 0.20 * E_max;
    E_target = 0.50 * E_max;
    RTE = 0.95;
    eta_c = sqrt(RTE);
    eta_d = sqrt(RTE);

    N = 24;
    P_grid = zeros(N,1);
    P_ch = zeros(N,1);
    P_dis = zeros(N,1);
    E = zeros(N,1);
    cost_hour = zeros(N,1);

    if numel(P_fcst) ~= N || numel(P_actual) ~= N || numel(P_demand) ~= N || numel(TOU_price) ~= N
        error('All day vectors must be length 24.');
    end

    E_prev = E_ini;
    future_excess = max(0, P_fcst - P_demand);

    for t = 1:N
        E_prev = min(max(E_prev, E_min), E_max);

        forecast_excess = max(0, P_fcst(t) - P_demand(t));
        actual_excess = max(0, P_actual(t) - P_demand(t));
        forecast_deficit = max(0, P_demand(t) - P_fcst(t));
        actual_deficit = max(0, P_demand(t) - P_actual(t));

        planned_pv_charge = min([forecast_excess, P_max, (E_max - E_prev) / eta_c]);
        actual_pv_charge = min([planned_pv_charge, actual_excess, (E_max - E_prev) / eta_c]);

        remaining_future_excess = 0;
        if t < N
            remaining_future_excess = sum(future_excess(t+1:end));
        end
        energy_needed_to_target = max(0, (E_target - (E_prev + eta_c * actual_pv_charge)) / eta_c);

        planned_grid_charge = 0;
        if is_offpeak(t) && E_prev + eta_c * actual_pv_charge < E_target
            if remaining_future_excess < energy_needed_to_target
                planned_grid_charge = min([P_max - actual_pv_charge, energy_needed_to_target - remaining_future_excess, (E_max - (E_prev + eta_c * actual_pv_charge)) / eta_c]);
            end
        end

        charge_power = actual_pv_charge + planned_grid_charge;
        discharge_power = 0;
        if is_onpeak(t)
            max_discharge = min([P_max, (E_prev + eta_c * charge_power - E_min) * eta_d, actual_deficit]);
            discharge_power = max(0, max_discharge);
        end

        P_ch(t) = charge_power;
        P_dis(t) = discharge_power;

        E_curr = E_prev + eta_c * P_ch(t) - P_dis(t) / eta_d;
        E_curr = min(max(E_curr, E_min), E_max);
        E(t) = E_curr;

        P_grid(t) = max(0, P_demand(t) - P_actual(t) + P_ch(t) - P_dis(t));
        cost_hour(t) = P_grid(t) * TOU_price(t);

        E_prev = E_curr;
    end
end
