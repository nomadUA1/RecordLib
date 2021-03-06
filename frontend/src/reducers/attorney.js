/**
 * manage changes to the state of the Attorney of this session.
 */

import { merge } from "lodash";

const initialAttorney = {
  hasBeenEdited: false, //Indicate if this has been edited by the user, to prevent overriding with defaults.
  editing: true,
  address: {
    line_one: "",
    city_state_zip: "",
  },
};

export default function attorneyReducer(state = initialAttorney, action) {
  switch (action.type) {
    case "ADD_ATTORNEY": {
      const { attorney } = action.payload;

      const newState = Object.assign({}, state, attorney);
      return newState;
    }
    case "UPDATE_ATTORNEY": {
      console.log("updating attorney.");
      const { update } = action.payload;
      console.log(action.payload);
      const newState = merge({}, state, update);
      console.log("new state");
      console.log(newState);
      return newState;
    }
    case "EDIT_ATTORNEY": {
      const { field, value } = action.payload;
      let newState;
      if (field.substring(0, 7) == "address") {
        const subfield = field.substring(8);
        newState = Object.assign(
          {},
          state,
          {
            address: Object.assign({}, state.address, {
              [subfield]: value,
            }),
          },
          { hasBeenEdited: true }
        );
      } else {
        newState = Object.assign(
          {},
          state,
          {
            [field]: value,
          },
          { hasBeenEdited: true }
        );
      }
      return newState;
    }
    case "TOGGLE_EDITING_ATTORNEY": {
      const { editing } = state;

      const newState = Object.assign({}, state, {
        editing: !editing,
      });
      return newState;
    }
    default: {
      return state;
    }
  }
}
