const SUBSCRIBERS_CONTAINER_CLASS = 'subscribers';

const SUBSCRIBER_CLASS = 'subscribers__item';
const SUBSCRIBER_ACTIVE_CLASS = `${SUBSCRIBER_CLASS}--active`;

const SUBSCRIBER_CALL_BUTTON_CLASS = 'subscribers__call-button';

const subscribersContainer = document.querySelector<HTMLUListElement>(`.${SUBSCRIBERS_CONTAINER_CLASS}`);

if (!subscribersContainer) {
  throw Error('Not found the subscribers container!');
}

const subscribers = subscribersContainer.querySelectorAll<HTMLLIElement>(`.${SUBSCRIBER_CLASS}`);

type IterateSubscriberCallback = (subscriber: HTMLLIElement, callButton: HTMLButtonElement) => void | boolean;
const goTroughSubscribers = (callback: IterateSubscriberCallback) => {
  for (const subscriber of subscribers) {
    const callButton = subscriber.querySelector<HTMLButtonElement>(`.${SUBSCRIBER_CALL_BUTTON_CLASS}`);

    if (!callButton) {
      throw Error('Not found a call button in a subscriber!');
    }

    const needBreak = callback(subscriber, callButton);

    if (needBreak) {
      break;
    }
  }
};

const getSubscriberData = (subscriber: HTMLElement): { id: string; fullName: string } => {
  const subscriberId = subscriber.dataset.subscriberId;
  const subscriberFullName = subscriber.dataset.subscriberFullName;

  if (!subscriberId || !subscriberFullName) {
    throw Error('Not found subscriber id or full name in dataset in the current subscriber!');
  }

  return { id: subscriberId, fullName: subscriberFullName };
};

export const markOnlineSubscribers = (ids: Record<string, true>): void => {
  goTroughSubscribers((subscriber, callButton) => {
    const { id: subscriberId } = getSubscriberData(subscriber);

    if (ids[subscriberId]) {
      subscriber.classList.add(SUBSCRIBER_ACTIVE_CLASS);
      callButton.disabled = false;
    } else {
      subscriber.classList.remove(SUBSCRIBER_ACTIVE_CLASS);
      callButton.disabled = true;
    }
  });
};

const onlineUsersHistory: Record<string, NodeJS.Timeout> = {};

export const markOnlineSubscriber = (id: string): void => {
  if (onlineUsersHistory[id]) {
    clearTimeout(onlineUsersHistory[id]);
    delete onlineUsersHistory[id];
    return;
  }

  goTroughSubscribers((subscriber, callButton) => {
    const { id: subscriberId } = getSubscriberData(subscriber);

    if (subscriberId === id) {
      subscriber.classList.add(SUBSCRIBER_ACTIVE_CLASS);
      callButton.disabled = false;

      return true;
    }
  });
};

export const discardOnlineSubscriber = (id: string): void => {
  const discardUserEvent = setTimeout((): void => {
    goTroughSubscribers((subscriber, callButton) => {
      const { id: subscriberId } = getSubscriberData(subscriber);

      if (subscriberId === id) {
        subscriber.classList.remove(SUBSCRIBER_ACTIVE_CLASS);
        callButton.disabled = true;

        return true;
      }
    });

    delete onlineUsersHistory[Number(discardUserEvent)];
  }, 10000);

  onlineUsersHistory[Number(discardUserEvent)] = discardUserEvent;
};

export const setCallButtonClickHandler = (callback: (id: string, fullName: string) => void): void => {
  goTroughSubscribers((subscriber, callButton) => {
    const { id: subscriberId, fullName: subscriberFullName } = getSubscriberData(subscriber);
    callButton.onclick = () => callback(subscriberId, subscriberFullName);
  });
};
