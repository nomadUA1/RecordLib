import * as api from "../api";
import { normalizeCRecord, CRECORD_ID } from "../normalize";
import { generateId } from "./helpers";

/**
 * a generic action creator for editing a field of
 * an entity in the store
 * @param  {string} entityName the key for this type of entity
 * in the store
 * @param  {string} entityId   the id of the specific entity
 * being edited
 * @param  {string} field      the key of the field being edited
 * @param  {string} value      the new value for the field
 * @return {Object}            an action whose payload holds
 * all the above values
 */
export function editField(entityName, entityId, field, value) {
  return {
    type: "EDIT_ENTITY_VALUE",
    payload: { entityName, entityId, field, value },
  };
}

export function toggleEditing(caseId) {
  return {
    type: "TOGGLE_EDITING",
    payload: { caseId },
  };
}

export function editSentenceLength(sentenceId, field, value) {
  return {
    type: "EDIT_SENTENCE_LENGTH",
    payload: { sentenceId, field, value },
  };
}

export function addCase(docket_number) {
  const newCase = {
    id: docket_number,
    docket_number,
    status: "",
    county: "",
    otn: "",
    dc: "",
    charges: [],
    total_fines: "",
    fines_paid: "",
    complaint_date: "",
    arrest_date: "",
    disposition_date: "",
    judge: "",
    judge_address: "",
    affiant: "",
    arresting_agency: "",
    arresting_agency_address: "",
    editing: true,
  };

  return {
    type: "ADD_ENTITY",
    payload: {
      entityName: "cases",
      entity: newCase,
      parentId: CRECORD_ID,
      parentEntityName: "cRecord",
      parentListKey: "cases",
    },
  };
}

export function addCharge(caseId) {
  const id = generateId();
  const newCharge = {
    id,
    offense: "",
    grade: "",
    statute: "",
    disposition: "",
    disposition_date: "",
    sentences: [],
  };

  return {
    type: "ADD_ENTITY",
    payload: {
      entityName: "charges",
      entity: newCharge,
      parentId: caseId,
      parentEntityName: "cases",
      parentListKey: "charges",
    },
  };
}

export function addSentence(chargeId) {
  const id = generateId();
  const SentenceLength = {
    min_time: "",
    max_time: "",
  };
  const newSentence = {
    id,
    sentence_date: "",
    sentence_type: "",
    sentence_period: "",
    sentence_length: SentenceLength,
  };

  return {
    type: "ADD_ENTITY",
    payload: {
      entityName: "sentences",
      entity: newSentence,
      parentId: chargeId,
      parentEntityName: "charges",
      parentListKey: "sentences",
    },
  };
}

export function updateAttorney(update) {
  return {
    type: "UPDATE_ATTORNEY",
    payload: { update },
  };
}

export function addAttorney(full_name) {
  const attorney = {
    id: full_name,
    full_name,
    address: {
      line_one: "",
      city_state_zip: "",
    },
    organization_phone: "",
    bar_id: "",
    organization: "",
    editing: true,
  };

  return {
    type: "ADD_ATTORNEY",
    payload: { attorney },
  };
}

export function toggleEditingAttorney() {
  return {
    type: "TOGGLE_EDITING_ATTORNEY",
    payload: {},
  };
}

export function editAttorney(field, value) {
  return {
    type: "EDIT_ATTORNEY",
    payload: { field, value },
  };
}

export function createNewServiceAgency(serviceAgency) {
  return {
    type: "NEW_SERVICE_AGENCY",
    payload: serviceAgency,
  };
}

export function updateServiceAgency(id, name) {
  return {
    type: "EDIT_SERVICE_AGENCY",
    payload: { id, name },
  };
}

export function deleteServiceAgency(id) {
  return {
    type: "DELETE_SERVICE_AGENCY",
    payload: { id },
  };
}
