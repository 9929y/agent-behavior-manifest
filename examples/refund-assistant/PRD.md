# PRD · Refund Assistant (fictional example)

> A fictional PRD for an online home-goods store, written the way PRDs usually are. It is
> deliberately incomplete: it has adjectives, missing edge cases, and unstated thresholds. It is
> the input for the worked example in this folder.

## 1. Problem

Support agents spend 40% of their time on refund requests. Most are simple: a damaged item, a late
delivery, the wrong size. Customers wait 2–3 days for an answer.

## 2. Goal

An AI assistant in the help-center chat that resolves simple refund requests instantly and hands
complex ones to a human agent with full context.

## 3. Users

- **Customers** who have placed an order and want money back.
- **Support agents** who handle escalated cases in the support console.
- **Finance**, which audits refunds monthly.

## 4. User stories

1. As a customer, when I open chat and say my item arrived damaged, the assistant finds my order, asks for a photo, and refunds me automatically if eligible.
2. As a customer, I can ask about the status of a refund I already requested.
3. As a support agent, when the assistant hands me a case, I see the order, what the customer said, what the assistant checked, and why it escalated.
4. As finance, every refund has a reason and an audit trail.

## 5. Functional requirements

- The assistant can look up the customer's orders (the customer is logged in).
- It can check the return policy: items are refundable within 30 days of delivery; final-sale items are not refundable; refunds go to the original payment method.
- It can issue refunds through the Payments API. **Auto-refunds are allowed up to $50 per order.** Above that, a human approves.
- It should be smart about detecting abuse (for example, customers with many refunds).
- It remembers past conversations so customers don't have to repeat themselves.
- It should respond in a friendly, empathetic tone.

## 6. Non-goals (v1)

- Exchanges and replacements.
- Changing shipping addresses or cancelling orders that haven't shipped.
- Store credit or discount codes.

## 7. Success metrics

- 60% of refund conversations resolved without a human.
- CSAT ≥ 4.3 for assistant-handled conversations.
- Refund error rate (wrong amount or ineligible refund) < 0.5%.

## 8. Open questions

- What counts as "many refunds"?
- Do we need the photo for every damage claim?
